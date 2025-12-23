# Image Analyzer

AI-powered image analysis using computer vision models.

## Setup

1. Create virtual environment:

   ```powershell
   python -m venv venv
   ```

2. Activate it:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   If error occurs:

   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   # Note: Git must be installed for the following line to work
   pip install git+https://github.com/openai/CLIP.git
   ```

4. Run:

   ```powershell
   python run.py
   ```

5. Open browser: `http://localhost:5000`

## Features

- Image captioning (BLIP)
- Object detection (YOLO)
- Attribute classification (CLIP)
- Location & weather extraction (EXIF + API)
- Time analysis

## Usage

1. Upload image
2. Click Analyze
3. View results

## Notes

- First run downloads models (1-2 GB, 5-15 min)
- First analysis is slower (model loading)
- Subsequent analyses are faster (5-10 sec)
- Works on CPU (GPU optional)

**Weather & Time Info:**

- Requires photos with GPS EXIF data
- Photos from smartphones usually have this
- Downloaded images often don't have EXIF data
- To test: use photos taken with your phone camera

## Troubleshooting

**Port in use:** Change port in `run.py`

**Failed fetch:** If something goes wrong try putting image second time

**Slow analysis:** Normal on first run, faster after
