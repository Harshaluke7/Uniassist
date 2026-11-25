# UniAssist

## New files
| File | Purpose |
|---|---|
| `pages/1_Report_Issue.py` | Text and/or photo complaint -> category, priority, location, department, letter, Submit |
| `pages/2_Computer_Vision.py` | Upload an image, see YOLO boxes (good for the viva) |
| `pages/3_Dashboard.py` | KPIs, charts, status editing, demo data |
| `shared.py` | Cached model loading shared by all pages |
| `complaint_logic.py` | Text classifier, fusion, priority, location, letter |
| `vision_engine.py` | YOLOv8 detection, Gemini furniture-condition check |
| `storage.py`, `dashboard.py` | CSV/Pandas storage (`data/complaints.csv`) and Plotly charts |
| `config.py` | Categories, campus locations, class-name rules, priority rules: edit for your campus |
| `train_yolo.py` | Fine-tune YOLOv8 in Colab, then copy `best.pt` into `models/` |
| `tests/test_logic.py` | `python tests/test_logic.py` |

