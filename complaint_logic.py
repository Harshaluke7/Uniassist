"""Text classification, multimodal fusion, priority rules, location extraction, complaint letter.
Heavy models are injected, so the pure functions here can be tested without them."""
import re

import config


class TextClassifier:
    """Classifies a complaint by cosine similarity to example sentences per category."""

    def __init__(self, model):
        self.model = model
        self.texts, self.labels = [], []
        for cat, meta in config.CATEGORIES.items():
            for ex in meta["examples"]:
                self.texts.append(ex)
                self.labels.append(cat)
        self.emb = model.encode(self.texts, convert_to_tensor=True, normalize_embeddings=True)

    def classify(self, text):
        from sentence_transformers import util
        q = self.model.encode(text, convert_to_tensor=True, normalize_embeddings=True)
        scores = util.cos_sim(q, self.emb)[0].tolist()
        best = {}
        for label, s in zip(self.labels, scores):
            best[label] = max(best.get(label, 0.0), s)
        ranking = sorted(best.items(), key=lambda kv: kv[1], reverse=True)
        return dict(category=ranking[0][0], score=ranking[0][1], ranking=ranking)


def extract_location(text):
    for loc in sorted(config.LOCATIONS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(loc) + r"\b", text or "", re.I):
            return loc
    return "Not specified"


def priority_for(category, issue_type, text):
    t = (text or "").lower()
    if any(k in t for k in config.HIGH_KEYWORDS):
        return "High"
    if issue_type in config.PRIORITY_BY_ISSUE:
        return config.PRIORITY_BY_ISSUE[issue_type]
    return config.PRIORITY_BASE.get(category, "Low")


def fuse(text_cls, cv_issue):
    """Combine the text result and the best image issue into one category.
    Cosine scores are not probabilities, so the text score is rescaled (0.6 similarity ~ full confidence)."""
    t = text_cls if text_cls and text_cls["score"] >= config.CAT_MIN_SCORE else None
    t_conf = min(1.0, t["score"] / 0.6) if t else 0.0

    if t and cv_issue:
        if t["category"] == cv_issue["category"]:
            return dict(category=t["category"], issue_type=cv_issue["issue_type"], confidence=min(1.0, max(t_conf, cv_issue["confidence"]) + 0.1),
                        agreement="Text and image agree", needs_review=False)
        use_cv = cv_issue["confidence"] >= t_conf
        return dict(category=cv_issue["category"] if use_cv else t["category"],
                    issue_type=cv_issue["issue_type"] if use_cv else f"{t['category']} complaint",
                    confidence=max(t_conf, cv_issue["confidence"]), agreement="Text and image disagree", needs_review=True)
    if cv_issue:
        return dict(category=cv_issue["category"], issue_type=cv_issue["issue_type"], confidence=cv_issue["confidence"],
                    agreement="Image only" if not text_cls else "Image only (text unclear)", needs_review=False)
    if t:
        return dict(category=t["category"], issue_type=f"{t['category']} complaint", confidence=t_conf,
                    agreement="Text only", needs_review=t_conf < 0.6)
    return dict(category="Other / General", issue_type="Unclassified", confidence=0.0, agreement="No clear signal", needs_review=True)


def build_letter(result, name="Student"):
    loc = result["location"]
    where = f" near {loc}" if loc != "Not specified" else ""
    desc = result.get("text") or f"An issue ({result['issue_type']}) was detected in the attached photograph."
    return (f"To,\nThe {result['department']},\nUniversity\n\n"
            f"Subject: Complaint regarding {result['issue_type'].lower()}{where}\n\n"
            f"Respected Sir/Madam,\n\nI would like to bring the following issue to your attention{where}.\n\n{desc}\n\n"
            f"Category: {result['category']}\nPriority: {result['priority']}\n\n"
            f"I kindly request you to look into this matter and take the necessary action at the earliest.\n\n"
            f"Yours sincerely,\n{name}\n")


class ComplaintAnalyzer:
    def __init__(self, text_clf, vision):
        self.text_clf, self.vision = text_clf, vision

    def analyze(self, text, image=None, location=None):
        text = (text or "").strip()
        t_cls = self.text_clf.classify(text) if text else None
        vis = self.vision.analyze(image) if image is not None else None
        cv_issue = max(vis["issues"], key=lambda i: i["confidence"]) if vis and vis["issues"] else None

        fused = fuse(t_cls, cv_issue)
        category = fused["category"]
        meta = config.CATEGORIES[category]
        return dict(text=text, **fused, location=location or extract_location(text),
                    priority=priority_for(category, fused["issue_type"], text),
                    department=meta["department"], action=meta["action"],
                    text_result=t_cls, cv_issue=cv_issue, vision=vis)
