"""Fine-tune YOLOv8 on your merged Roboflow export (run in Google Colab with a GPU).
1. Export the merged dataset from Roboflow in 'YOLOv8' format and unzip it as ./dataset (it contains data.yaml).
2. pip install ultralytics   then   python train_yolo.py
3. Copy runs/detect/train/weights/best.pt to uniassist_vision/models/best.pt
"""
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.train(data="dataset/data.yaml", epochs=40, imgsz=640, batch=16)
metrics = model.val()  # precision, recall, mAP; confusion matrix plots are saved in runs/detect/
print("mAP50:", metrics.box.map50, "mAP50-95:", metrics.box.map)
