"""Computer vision: YOLOv8 detection, mapping to campus issues, Gemini vision for furniture condition."""
import json
import re

from PIL import Image, ImageOps

import config
import gemini_client


def normalize(label):
    return label.lower().replace(" ", "_").replace("-", "_")


def label_to_issue(label):
    """YOLO class name -> (category, issue_type) or None."""
    norm = normalize(label)
    if norm in config.IGNORE_LABELS:
        return None
    for keywords, category, issue in config.LABEL_RULES:
        if any(k in norm for k in keywords):
            return category, issue
    return None


def preprocess(img):
    """Fix phone-photo rotation, force RGB, shrink very large images."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    if max(img.size) > config.MAX_IMAGE_SIDE:
        img.thumbnail((config.MAX_IMAGE_SIDE, config.MAX_IMAGE_SIDE))
    return img


def _parse_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


class VisionEngine:
    def __init__(self, weights=None):
        from ultralytics import YOLO
        path = weights or (str(config.CUSTOM_WEIGHTS) if config.CUSTOM_WEIGHTS.exists() else config.DEFAULT_WEIGHTS)
        self.weights = path
        self.custom = path != config.DEFAULT_WEIGHTS
        self.model = YOLO(path)

    def detect(self, img, conf=None):
        res = self.model.predict(img, conf=conf or config.YOLO_CONF, verbose=False)[0]
        annotated = Image.fromarray(res.plot()[..., ::-1])  # BGR -> RGB
        dets = []
        for b in res.boxes:
            x1, y1, x2, y2 = (int(v) for v in b.xyxy[0].tolist())
            dets.append(dict(label=res.names[int(b.cls[0])], confidence=round(float(b.conf[0]), 3), box=(x1, y1, x2, y2)))
        return annotated, dets

    def assess_furniture(self, img, box):
        """Ask Gemini whether the cropped furniture is broken. Returns (broken|None, description)."""
        prompt = ('Look at this piece of furniture. Is it broken or damaged (missing parts, cracks, torn, collapsed)? '
                  'Reply only with JSON: {"broken": true or false, "description": "one short sentence"}')
        text, err = gemini_client.generate([prompt, img.crop(box)])
        data = _parse_json(text)
        if not data:
            return None, err or "Gemini gave no usable answer"
        return bool(data.get("broken")), str(data.get("description", ""))

    def analyze(self, img, conf=None):
        """Full image analysis. Returns dict(image, annotated, detections, issues, notes)."""
        img = preprocess(img)
        annotated, dets = self.detect(img, conf)
        issues, notes, furniture = [], [], []
        for d in dets:
            mapped = label_to_issue(d["label"])
            if mapped:
                d["issue"] = mapped[1]
                issues.append(dict(category=mapped[0], issue_type=mapped[1], confidence=d["confidence"],
                                   label=d["label"], source="YOLO"))
            elif normalize(d["label"]) in config.FURNITURE_LABELS:
                furniture.append(d)
        # Detect-then-assess: check the two largest furniture items for damage
        furniture.sort(key=lambda d: (d["box"][2] - d["box"][0]) * (d["box"][3] - d["box"][1]), reverse=True)
        for d in furniture[:2]:
            broken, desc = self.assess_furniture(img, d["box"])
            if broken is None:
                notes.append(f"{d['label']} detected, condition not assessed ({desc}).")
            elif broken:
                d["issue"] = "Broken furniture"
                issues.append(dict(category="Infrastructure", issue_type="Broken furniture", confidence=d["confidence"],
                                   label=d["label"], source="YOLO + Gemini", note=desc))
                notes.append(f"{d['label']}: broken. {desc}")
            else:
                notes.append(f"{d['label']}: looks intact. {desc}")
        return dict(image=img, annotated=annotated, detections=dets, issues=issues, notes=notes)
