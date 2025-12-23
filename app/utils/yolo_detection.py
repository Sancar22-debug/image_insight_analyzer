"""
YOLO Object Detection - YOLOv8m
"""
from ultralytics import YOLO
import os

_model = None

def get_model():
    global _model
    if _model is None:
        model_path = os.path.join('app', 'models', 'yolo_best.pt')
        if os.path.exists(model_path):
            _model = YOLO(model_path)
        else:
            _model = YOLO('yolov8n.pt')
    return _model

def detect_objects(image_path, confidence_threshold=0.5):
    try:
        model = get_model()
        results = model(image_path, conf=confidence_threshold)
        detections = []
        for result in results:
            boxes = result.boxes
            for i in range(len(boxes)):
                detections.append({
                    'class': result.names[int(boxes.cls[i])],
                    'confidence': float(boxes.conf[i]),
                    'bbox': boxes.xyxy[i].tolist()
                })
        return detections
    except:
        return []

def count_objects(detections):
    counts = {}
    for det in detections:
        counts[det['class']] = counts.get(det['class'], 0) + 1
    return counts

def analyze_objects(counts):
    analysis = {'scene_type': 'general', 'reasoning': [], 'activity_level': 'unknown'}
    total = sum(counts.values())
    
    vehicles = counts.get('car', 0) + counts.get('truck', 0) + counts.get('bus', 0)
    if vehicles >= 5:
        analysis['reasoning'].append(f"Many vehicles ({vehicles}) - urban/traffic area")
        analysis['scene_type'] = 'urban'
    
    people = counts.get('person', 0)
    if people >= 5:
        analysis['reasoning'].append(f"Multiple people ({people}) - busy area")
        analysis['activity_level'] = 'busy'
    
    animals = counts.get('dog', 0) + counts.get('cat', 0) + counts.get('cow', 0) + counts.get('horse', 0)
    if animals >= 2:
        analysis['reasoning'].append(f"Animals detected ({animals}) - park or farm setting")
    
    indoor = counts.get('chair', 0) + counts.get('couch', 0) + counts.get('bed', 0) + counts.get('tv', 0)
    if indoor >= 2:
        analysis['reasoning'].append("Indoor furniture detected")
        analysis['scene_type'] = 'indoor'
    
    if total == 0:
        analysis['reasoning'].append("No common objects - landscape or abstract scene")
    
    return analysis
