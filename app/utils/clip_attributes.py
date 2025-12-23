"""
OpenCLIP Attribute Classification - ViT-L/14
"""
import torch
from PIL import Image

_model = None
_preprocess = None
_tokenizer = None
_device = None

def get_model():
    global _model, _preprocess, _tokenizer, _device
    if _model is None:
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            import open_clip
            _model, _, _preprocess = open_clip.create_model_and_transforms('ViT-L-14', pretrained='laion2b_s32b_b82k')
            _tokenizer = open_clip.get_tokenizer('ViT-L-14')
            _model.to(_device).eval()
        except:
            import clip
            _model, _preprocess = clip.load("ViT-B/32", device=_device)
            _tokenizer = clip.tokenize
    return _model, _preprocess, _tokenizer, _device

def classify_attributes(image_path):
    try:
        model, preprocess, tokenizer, device = get_model()
        image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

        attributes = {
            'setting': ['indoor', 'outdoor'],
            'time_of_day': ['daytime', 'nighttime', 'sunrise', 'sunset'],
            'weather': ['sunny', 'cloudy', 'rainy', 'snowy', 'foggy'],
            'season': ['spring', 'summer', 'fall', 'winter'],
            'lighting': ['bright', 'dim', 'natural light', 'artificial light'],
            'mood': ['happy', 'calm', 'energetic', 'peaceful', 'dramatic'],
            'scene_type': ['urban', 'rural', 'beach', 'mountain', 'forest', 'desert'],
            'activity': ['busy', 'calm', 'empty']
        }

        results = {}
        for category, options in attributes.items():
            prompts = [f"a photo that is {opt}" for opt in options]
            text_inputs = tokenizer(prompts).to(device)

            with torch.no_grad():
                image_features = model.encode_image(image)
                text_features = model.encode_text(text_inputs)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                text_features /= text_features.norm(dim=-1, keepdim=True)
                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

            values, indices = similarity[0].topk(1)
            results[category] = {'value': options[indices[0].item()], 'confidence': float(values[0])}

        return results
    except:
        return {}
