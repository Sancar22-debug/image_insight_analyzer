"""
BLIP Image Captioning Module
Generates natural language descriptions of images using BLIP
"""
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# Global model instances
_processor = None
_model = None
_device = None

def get_model():
    """Load BLIP model (singleton pattern)"""
    global _processor, _model, _device
    if _model is None:
        _device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            _processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            _model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            _model.to(_device)
        except Exception as e:
            print(f"Error loading BLIP model: {e}")
            raise
    return _processor, _model, _device

def generate_caption(image_path, max_length=50, num_beams=4):
    """
    Generates a natural language caption for an image

    Args:
        image_path: Path to the image file
        max_length: Maximum length of generated caption
        num_beams: Number of beams for beam search (higher = better quality, slower)

    Returns:
        String caption describing the image
    """
    try:
        processor, model, device = get_model()

        # Load and process image
        image = Image.open(image_path).convert('RGB')
        inputs = processor(image, return_tensors="pt").to(device)

        # Generate caption
        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=num_beams,
                early_stopping=True
            )

        # Decode caption
        caption = processor.decode(output[0], skip_special_tokens=True)

        return caption

    except Exception as e:
        print(f"Error generating caption: {e}")
        return "Unable to generate caption"

def generate_detailed_caption(image_path):
    """
    Generates a more detailed caption with higher quality settings

    Args:
        image_path: Path to the image file

    Returns:
        Detailed string caption
    """
    return generate_caption(image_path, max_length=75, num_beams=5)

def answer_question(image_path, question):
    """
    Answer a question about the image using BLIP VQA (Visual Question Answering)

    Args:
        image_path: Path to the image file
        question: Question to ask about the image

    Returns:
        Answer string
    """
    try:
        # Note: This would require BLIP VQA model
        # For now, we'll use the caption model with conditional generation
        processor, model, device = get_model()

        image = Image.open(image_path).convert('RGB')
        inputs = processor(image, question, return_tensors="pt").to(device)

        with torch.no_grad():
            output = model.generate(**inputs, max_length=50)

        answer = processor.decode(output[0], skip_special_tokens=True)
        return answer

    except Exception as e:
        print(f"Error answering question: {e}")
        return "Unable to answer question"
