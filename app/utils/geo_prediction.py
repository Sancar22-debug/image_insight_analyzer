"""
Geo Prediction using StreetCLIP
"""
import torch
from PIL import Image

_model = None
_processor = None
_device = None

COUNTRIES = [
    "United States", "United Kingdom", "Canada", "Australia", "Germany",
    "France", "Italy", "Spain", "Japan", "China", "South Korea", "India",
    "Brazil", "Mexico", "Russia", "Netherlands", "Sweden", "Norway",
    "Poland", "Switzerland", "Portugal", "Greece", "Turkey", "Thailand",
    "Indonesia", "Singapore", "South Africa", "Argentina", "New Zealand"
]

def get_model():
    global _model, _processor, _device
    if _model is None:
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            from transformers import CLIPProcessor, CLIPModel
            _model = CLIPModel.from_pretrained("geolocal/StreetCLIP")
            _processor = CLIPProcessor.from_pretrained("geolocal/StreetCLIP")
            _model.to(_device).eval()
        except:
            print("StreetCLIP not found or error, falling back to OpenCLIP ViT-B-32")
            import open_clip
            _model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
            _processor = preprocess
            _model.to(_device).eval()
    return _model, _processor, _device

def predict_country(image_path, top_k=5):
    try:
        model, processor, device = get_model()
        image = Image.open(image_path).convert('RGB')
        
        prompts = [f"a street view photo from {c}" for c in COUNTRIES]
        inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = outputs.logits_per_image.softmax(dim=1)
        
        values, indices = probs[0].topk(top_k)
        return [{'country': COUNTRIES[indices[i].item()], 'confidence': float(values[i])} for i in range(top_k)]
    except:
        return []

def get_geo_prediction(image_path):
    predictions = predict_country(image_path, top_k=5)
    return {
        'predictions': predictions,
        'top_country': predictions[0] if predictions else None,
        'reasoning': 'Based on visual patterns' if predictions else ''
    }
