"""Central settings for UniAssist Vision. Edit the lists below to match your campus."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
MODELS_DIR = BASE_DIR / "models"
COMPLAINTS_PATH = DATA_DIR / "complaints.csv"

# ---- NLP ----
EMBED_MODEL = "all-MiniLM-L6-v2"
CAT_MIN_SCORE = 0.30  # below this, a text complaint is filed as "Other / General"

# ---- Gemini ----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

# ---- Vision ----
CUSTOM_WEIGHTS = MODELS_DIR / "best.pt"   # put your fine-tuned YOLOv8 weights here
DEFAULT_WEIGHTS = "yolov8n.pt"            # COCO model, downloaded automatically
YOLO_CONF = 0.25
MAX_IMAGE_SIDE = 1280

# Detection labels that are not problems by themselves
IGNORE_LABELS = {"garbage_bin", "bin", "bin_body", "normal", "clean"}

# (keywords found in the YOLO class name, category, issue type) - first match wins
LABEL_RULES = [
    (("overflow", "overload"), "Cleanliness", "Overflowing bin"),
    (("broken_furniture", "broken_chair", "broken_bench", "broken_desk", "damaged_furniture", "defect", "broken", "damaged"), "Infrastructure", "Broken furniture"),
    (("garbage", "trash", "litter", "waste", "plastic"), "Cleanliness", "Garbage"),
    (("leak", "water", "pipe"), "Water", "Water leakage"),
    (("crack", "wall", "spalling", "peeling", "damp", "mold", "mould", "paint"), "Infrastructure", "Wall damage"),
    (("broken_light", "lamp", "bulb"), "Electrical", "Broken light"),
    (("electrical", "wire", "socket", "switch", "hazard", "board", "plug", "cable"), "Electrical", "Electrical fault"),
    (("computer", "monitor", "keyboard", "mouse", "cpu", "equipment", "projector", "screen"), "IT / ERP", "Lab equipment issue"),
]
# COCO furniture classes: YOLO finds the object, Gemini vision judges its condition
FURNITURE_LABELS = {"chair", "couch", "bench", "dining_table", "table", "almirah"}

# ---- Complaint categories (text classifier uses the examples) ----
CATEGORIES = {
    "Cleanliness": dict(department="Housekeeping / Sanitation", action="Forward to the housekeeping team for cleaning.",
        examples=["There is garbage near the library", "The dustbin is overflowing", "The washrooms are dirty",
                  "Waste is lying around the cafeteria", "The corridor smells bad and needs cleaning"]),
    "Infrastructure": dict(department="Estate / Maintenance Office", action="Forward to the maintenance office for inspection and repair.",
        examples=["The bench in the classroom is broken", "There is a crack in the wall", "The door of the lab is damaged",
                  "The ceiling is damaged and falling", "The desks in the lecture hall are broken"]),
    "Electrical": dict(department="Electrical Maintenance", action="Send an electrician to inspect and fix the fault.",
        examples=["The classroom lights are not working", "The fan is not working", "The power socket is damaged",
                  "There is no electricity in the hostel room", "The projector is not turning on"]),
    "Water": dict(department="Plumbing / Water Works", action="Send a plumber to check the leakage or supply.",
        examples=["There is water leaking in my hostel", "The water cooler is leaking", "No water supply in the washroom",
                  "The tap is broken and dripping", "Water is dripping from the ceiling"]),
    "Hostel": dict(department="Hostel Warden Office", action="Forward to the hostel warden.",
        examples=["The hostel mess food quality is poor", "My hostel room has no proper bed", "Wi-Fi is not working in the hostel",
                  "There is noise in the hostel at night", "Laundry service is not available"]),
    "Academic": dict(department="Academic Section", action="Forward to the academic section.",
        examples=["My marks are not updated", "The timetable has a clash", "The faculty is not taking classes",
                  "Exam hall ticket is not available", "Attendance is wrongly recorded"]),
    "Transport": dict(department="Transport Office", action="Forward to the transport office.",
        examples=["The college bus is always late", "The bus route needs a new stop", "The bus is overcrowded",
                  "The driver is driving rashly", "Bus pass is not issued"]),
    "Safety": dict(department="Campus Security", action="Alert campus security immediately.",
        examples=["There is a stray dog near the ground", "The street light near the gate is not working at night",
                  "A pathway is blocked and unsafe", "I feel unsafe walking near the parking area", "Sharp objects are lying on the road"]),
    "IT / ERP": dict(department="IT Support Cell", action="Forward to the IT support cell.",
        examples=["I cannot log in to the ERP portal", "The Wi-Fi is very slow in the library", "The lab computers are not working",
                  "The student portal is showing an error", "My email account is locked"]),
    "Other / General": dict(department="Administration Office", action="Forward to the administration office for review.", examples=[]),
}

# Campus places recognised in complaint text (edit to your campus; longer names are matched first)
LOCATIONS = ["Library", "Cafeteria", "Canteen", "Girls Hostel", "Boys Hostel", "Hostel A", "Hostel B", "Hostel C",
             "A Block", "B Block", "C Block", "L Block", "Admin Block", "Main Gate", "Parking", "Playground",
             "Auditorium", "Computer Lab", "Seminar Hall", "Classroom"]

# ---- Priority rules ----
PRIORITY_BASE = {"Safety": "High", "Electrical": "Medium", "Water": "Medium", "Infrastructure": "Medium", "Hostel": "Medium",
                 "IT / ERP": "Medium", "Transport": "Medium", "Cleanliness": "Low", "Academic": "Low", "Other / General": "Low"}
PRIORITY_BY_ISSUE = {"Overflowing bin": "Medium", "Garbage": "Low", "Water leakage": "Medium", "Wall damage": "Medium",
                     "Broken furniture": "Medium", "Broken light": "Medium", "Electrical fault": "High", "Lab equipment issue": "Medium"}
HIGH_KEYWORDS = ["spark", "short circuit", "short-circuit", "shock", "fire", "smoke", "exposed wire", "naked wire", "flood",
                 "gas leak", "collapse", "injur", "danger", "unsafe", "hazard"]

STATUSES = ["Pending", "In Progress", "Resolved"]
