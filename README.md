# BLOOM.ID

BLOOM.ID is a lightweight flower identification web app powered by a TensorFlow Lite CNN model. Users can upload a flower image, get a prediction with confidence, view a short explanation, check local weather conditions, and ask a flower expert chatbot for care tips and facts.

## Features

- Flower image recognition using a trained CNN model in `model/flower_cnn.tflite`
- Confidence scoring and flower details for each prediction
- Weather lookup by city using Open-Meteo / AgroMonitoring APIs
- AI-powered flower advice via Hugging Face text generation/chat completions
- Neo-brutalist UI with a playful botanical theme

## Tech Stack

- Python
- Flask
- TensorFlow Lite / ai-edge-litert
- NumPy
- Pillow
- Hugging Face Inference Client

## Project Structure

```text
BLOOM/
├── app.py                 # Flask application and prediction logic
├── requirement.txt        # Python dependencies
├── render.yaml            # Render deployment config
├── model/
│   ├── flower_cnn.keras
│   └── flower_cnn.tflite
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── index.html
├── .env.example           # optional local env template (if added manually)
└── README.md
```

## Setup

1. Clone the repository:

```bash
git clone https://github.com/subhadip-some/BLOOM.ID.git
cd BLOOM.ID
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirement.txt
```

4. Add environment variables as needed:

Create a `.env` file in the project root:

```env
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
HF_MODEL=openai/gpt-oss-120b
AGROMONITORING_API_KEY=your_agromonitoring_api_key
```

Notes:
- `HUGGINGFACEHUB_API_TOKEN` is required only for the flower expert chatbot.
- `AGROMONITORING_API_KEY` is required for the weather feature.
- If the model token or weather key is absent, the app will fall back to limited behavior instead of crashing.

## Run Locally

Start the app:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## How It Works

- Upload a flower photo from the browser.
- The app preprocesses the image to a fixed 224x224 RGB size.
- The TFLite model classifies the image into one of five classes:
  - Lilly
  - Lotus
  - Orchid
  - Sunflower
  - Tulip
- The result includes a flower name, emoji, confidence score, and explanation.
- Weather data can be fetched for a city and passed into the chatbot context for plant-care recommendations.

## Deployment

This project is configured for Render via `render.yaml`.

```bash
git push
```

Then deploy the app on Render with the included configuration. The app is started with:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120
```

## Usage Tips

- Use clear, front-facing flower photos for better classification results.
- Add a valid Hugging Face token for richer botanical answers.
- The weather box can help tailor watering and placement suggestions.

## License

This project is provided as-is for educational and prototype use.

## Acknowledgements

- TensorFlow Lite model support via `ai-edge-litert`
- Weather service via Open-Meteo and AgroMonitoring APIs
- Hugging Face model access for conversational plant guidance
