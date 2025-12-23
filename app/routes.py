"""
Flask Routes for Image Insight Analyzer
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import traceback

from app.utils.yolo_detection import detect_objects, count_objects, analyze_objects
from app.utils.clip_attributes import classify_attributes
from app.utils.blip_caption import generate_caption
from app.utils.exif_location import extract_location, get_datetime
from app.utils.weather_api import get_weather
from app.utils.time_api import analyze_photo_time
from app.utils.visual_analysis import get_visual_predictions
from app.utils.geo_prediction import get_geo_prediction

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    print("Received analysis request...")
    try:
        file = request.files.get('file') or request.files.get('image')
        if not file or file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"File saved to: {filepath}")

        analysis = {'filename': filename}

        # Caption
        try:
            print("Generating caption...")
            analysis['caption'] = generate_caption(filepath, max_length=30, num_beams=2)
            print(f"Caption generated: {analysis['caption']}")
        except Exception as e:
            print(f"Caption error: {e}")
            traceback.print_exc()
            analysis['caption'] = None

        # Objects
        try:
            print("Detecting objects...")
            detections = detect_objects(filepath, confidence_threshold=0.25)
            counts = count_objects(detections)
            analysis['objects'] = [{'class': k, 'count': v} for k, v in counts.items()]
            analysis['object_analysis'] = analyze_objects(counts)
            print(f"Objects detected: {counts}")
        except Exception as e:
            print(f"Object detection error: {e}")
            traceback.print_exc()
            analysis['objects'] = []
            analysis['object_analysis'] = {}

        # Attributes
        try:
            print("Classifying attributes...")
            analysis['attributes'] = classify_attributes(filepath)
            print(f"Attributes: {analysis['attributes']}")
        except Exception as e:
            print(f"Attribute classification error: {e}")
            traceback.print_exc()
            analysis['attributes'] = {}

        # Visual predictions
        try:
            print("Getting visual predictions...")
            analysis['visual_predictions'] = get_visual_predictions(filepath)
            print(f"Visual predictions: {analysis['visual_predictions']}")
        except Exception as e:
            print(f"Visual prediction error: {e}")
            traceback.print_exc()
            analysis['visual_predictions'] = {}

        # Geo prediction
        try:
            print("Getting geo prediction...")
            analysis['geo_prediction'] = get_geo_prediction(filepath)
            print(f"Geo prediction: {analysis['geo_prediction']}")
        except Exception as e:
            print(f"Geo prediction error: {e}")
            traceback.print_exc()
            analysis['geo_prediction'] = {}

        # EXIF location
        try:
            print("Extracting EXIF location...")
            location = extract_location(filepath)
            if location:
                analysis['location'] = location
                analysis['has_exif_location'] = True
                try:
                    analysis['weather'] = get_weather(location)
                except Exception as e:
                    print(f"Weather API error: {e}")
                try:
                    photo_datetime = get_datetime(filepath)
                    if photo_datetime:
                        analysis['time_info'] = analyze_photo_time(photo_datetime)
                except Exception as e:
                    print(f"Time analysis error: {e}")
            else:
                analysis['has_exif_location'] = False
        except Exception as e:
            print(f"EXIF extraction error: {e}")
            traceback.print_exc()
            analysis['has_exif_location'] = False

        print("Analysis complete, returning results...")
        return jsonify(analysis)

    except Exception as e:
        print(f"Fatal error in analyze: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
