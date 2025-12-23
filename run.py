"""
Simple run script for Image Insight Analyzer
"""
from app.routes import app

if __name__ == '__main__':
    print("=" * 60)
    print("🔍 Image Insight Analyzer")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

