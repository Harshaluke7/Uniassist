# UniAssist Vision: drop-in files for your existing UniAssist folder

## Install (do this in order)
1. **Back up** your current `app.py` (this zip replaces it with the same app, lightly patched).
2. Unzip into your existing UniAssist folder, next to `embeddings.pkl` and `responses.pkl`.
3. Copy `.env.example` to `.env` and set `GEMINI_API_KEY`. The key is no longer written inside `app.py`.
4. In your activated venv: `pip install -r requirements.txt` (replaces/extends your old requirements).
5. `streamlit run app.py` from that folder.

## What changed in your app.py (only 3 things)
- The Gemini key is read from the `GEMINI_API_KEY` environment variable instead of being hard-coded.
- `.env` is loaded at the top (`load_dotenv()`).
- The model and the `.pkl` files are loaded through `shared.py` (cached), so the new pages reuse the same MiniLM model. Your chat logic, threshold (0.4), `enhance_response` and all your styling are untouched.

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

## Notes
- Without `models/best.pt` the vision pages use the generic COCO model (only chairs, benches, tables). Train on your merged dataset to detect garbage, bins, leaks and wall cracks.
- The dashboard has no login. Add one before sharing the app.
