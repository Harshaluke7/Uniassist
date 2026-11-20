"""Complaint storage in a CSV file, handled with pandas."""
import random
from datetime import datetime, timedelta

import pandas as pd

import config

COLUMNS = ["id", "timestamp", "text", "category", "issue_type", "location", "priority", "department", "status",
           "text_confidence", "cv_label", "cv_confidence", "agreement", "image_path", "source"]


def load():
    path = config.COMPLAINTS_PATH
    if not path.exists():
        return pd.DataFrame(columns=COLUMNS)
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601")  # accepts both "T" and space separators
    return df


def _save(df):
    config.COMPLAINTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    df[COLUMNS].to_csv(config.COMPLAINTS_PATH, index=False)


def _next_id(df):
    nums = pd.to_numeric(df["id"].astype(str).str.extract(r"(\d+)")[0], errors="coerce").dropna()
    return f"CMP-{int(nums.max()) + 1 if len(nums) else 1:04d}"


def add_complaint(result, image=None, source="live"):
    """result: output of ComplaintAnalyzer.analyze. Saves the original photo too. Returns the new id."""
    df = load()
    cid = _next_id(df)
    image_path = ""
    if image is not None:
        config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        p = config.UPLOAD_DIR / f"{cid}.jpg"
        image.convert("RGB").save(p, quality=90)
        image_path = str(p)
    cv = result.get("cv_issue") or {}
    tr = result.get("text_result") or {}
    row = dict(id=cid, timestamp=datetime.now().isoformat(timespec="seconds"), text=result["text"], category=result["category"],
               issue_type=result["issue_type"], location=result["location"], priority=result["priority"],
               department=result["department"], status="Pending", text_confidence=round(tr.get("score", 0.0), 3),
               cv_label=cv.get("label", ""), cv_confidence=cv.get("confidence", ""), agreement=result["agreement"],
               image_path=image_path, source=source)
    new_df = pd.DataFrame([row], columns=COLUMNS)
    combined = new_df if df.empty else pd.concat([df, new_df], ignore_index=True)
    _save(combined)
    return cid


def update_statuses(mapping):
    df = load()
    for cid, status in mapping.items():
        df.loc[df["id"] == cid, "status"] = status
    _save(df)


def seed_demo_data(n=40):
    """Fake rows so the dashboard looks populated for a demo. They are flagged source='demo'."""
    rng = random.Random(7)
    issues = [("Cleanliness", "Garbage", "Library"), ("Cleanliness", "Overflowing bin", "Cafeteria"), ("Infrastructure", "Broken furniture", "C Block"),
              ("Infrastructure", "Wall damage", "L Block"), ("Water", "Water leakage", "Hostel A"), ("Electrical", "Broken light", "Classroom"),
              ("Electrical", "Electrical fault", "Hostel B"), ("IT / ERP", "IT / ERP complaint", "Computer Lab"), ("Hostel", "Hostel complaint", "Hostel A"),
              ("Transport", "Transport complaint", "Main Gate"), ("Safety", "Safety complaint", "Parking")]
    weights = [5, 4, 5, 3, 4, 3, 1, 3, 3, 2, 1]
    df = load()
    start = int(_next_id(df).split("-")[1])
    rows = []
    for i in range(n):
        cat, issue, loc = rng.choices(issues, weights)[0]
        has_cv = cat in ("Cleanliness", "Infrastructure", "Water", "Electrical")
        rows.append(dict(id=f"CMP-{start + i:04d}", timestamp=(datetime.now() - timedelta(days=rng.randint(0, 13), hours=rng.randint(0, 23))).isoformat(timespec="seconds"),
                         text=f"Demo complaint: {issue.lower()} at {loc}", category=cat, issue_type=issue, location=loc,
                         priority=rng.choices(["Low", "Medium", "High"], [3, 5, 2])[0], department=config.CATEGORIES[cat]["department"],
                         status=rng.choices(config.STATUSES, [4, 2, 4])[0], text_confidence=round(rng.uniform(0.4, 0.8), 3),
                         cv_label=issue.lower().replace(" ", "_") if has_cv else "", cv_confidence=round(rng.uniform(0.6, 0.95), 3) if has_cv else "",
                         agreement="Text and image agree" if has_cv else "Text only", image_path="", source="demo"))
    new_df = pd.DataFrame(rows, columns=COLUMNS)
    combined = new_df if df.empty else pd.concat([df, new_df], ignore_index=True)
    _save(combined)


def clear_demo():
    df = load()
    _save(df[df["source"] != "demo"])
