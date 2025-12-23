"""
Visual Analysis - Time and Season from image pixels
"""
import cv2
import numpy as np

def predict_time_of_day(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {'prediction': 'unknown', 'confidence': 0, 'reasoning': 'Unable to load'}
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        brightness = np.mean(hsv[:, :, 2])
        
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        r, g, b = np.mean(rgb[:,:,0]), np.mean(rgb[:,:,1]), np.mean(rgb[:,:,2])
        warm_score = (r + g * 0.5) / (b + 1)
        
        if brightness < 50:
            return {'prediction': 'night', 'confidence': 0.85, 'reasoning': f'Very dark ({brightness:.0f}/255)'}
        elif brightness < 80:
            return {'prediction': 'evening', 'confidence': 0.7, 'reasoning': f'Low brightness ({brightness:.0f}/255)'}
        elif warm_score > 2.5 and brightness < 160:
            return {'prediction': 'sunrise/sunset', 'confidence': 0.75, 'reasoning': f'Warm colors with moderate light'}
        elif brightness > 150:
            return {'prediction': 'daytime', 'confidence': 0.8, 'reasoning': f'Bright ({brightness:.0f}/255)'}
        else:
            return {'prediction': 'daytime', 'confidence': 0.6, 'reasoning': f'Moderate brightness'}
    except:
        return {'prediction': 'unknown', 'confidence': 0, 'reasoning': 'Analysis failed'}

def predict_season(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {'prediction': 'unknown', 'confidence': 0, 'reasoning': 'Unable to load'}
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        h, s, v = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
        
        # Green detection
        green_mask = (h > 35) & (h < 85) & (s > 40)
        green_ratio = np.sum(green_mask) / green_mask.size
        
        # Brown/orange (fall)
        brown_mask = (h > 10) & (h < 30) & (s > 50)
        brown_ratio = np.sum(brown_mask) / brown_mask.size
        
        # White (winter)
        white_mask = (s < 40) & (v > 180)
        white_ratio = np.sum(white_mask) / white_mask.size
        
        if white_ratio > 0.25:
            return {'prediction': 'winter', 'confidence': 0.8, 'reasoning': f'Snow/white coverage ({white_ratio*100:.0f}%)'}
        elif brown_ratio > 0.15:
            return {'prediction': 'fall', 'confidence': 0.75, 'reasoning': f'Fall colors detected ({brown_ratio*100:.0f}%)'}
        elif green_ratio > 0.25:
            return {'prediction': 'summer', 'confidence': 0.7, 'reasoning': f'Green vegetation ({green_ratio*100:.0f}%)'}
        elif green_ratio > 0.1:
            return {'prediction': 'spring', 'confidence': 0.6, 'reasoning': f'Some vegetation ({green_ratio*100:.0f}%)'}
        else:
            return {'prediction': 'unknown', 'confidence': 0.4, 'reasoning': 'Low vegetation - indoor or urban'}
    except:
        return {'prediction': 'unknown', 'confidence': 0, 'reasoning': 'Analysis failed'}

def get_visual_predictions(image_path):
    return {
        'time_of_day': predict_time_of_day(image_path),
        'season': predict_season(image_path)
    }
