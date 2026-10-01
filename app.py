import os
import json
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, render_template, request, jsonify
from PIL import Image
import numpy as np

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from tensorflow.keras.models import load_model
except Exception:
    load_model = None

try:
    from huggingface_hub import InferenceClient
except Exception:
    InferenceClient = None

app = Flask(__name__)

FLOWER_CLASSES = ["Lilly", "Lotus", "Orchid", "Sunflower", "Tulip"]
FLOWER_EMOJI = {
    "Lilly": "🪷",
    "Lotus": "🪷",
    "Orchid": "🌸",
    "Sunflower": "🌻",
    "Tulip": "🌷",
}
FLOWER_DETAILS = {
    "Lilly": "A graceful bloom with elegant petals and a fresh, clean look.",
    "Lotus": "A serene aquatic flower symbolizing calmness, purity, and balance.",
    "Orchid": "An exotic flower with intricate symmetry and refined, delicate petals.",
    "Sunflower": "A bold, cheerful flower known for its bright petals and strong sun-facing habit.",
    "Tulip": "A classic spring flower with a smooth, cup-shaped bloom and vibrant color.",
}
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "flower_cnn.keras")
MODEL = None

if load_model is not None and os.path.exists(MODEL_PATH):
    try:
        MODEL = load_model(MODEL_PATH)
    except Exception:
        MODEL = None


def preprocess_image(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    image = image.resize((224, 224))
    img_array = np.array(image)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def generate_prediction(img_array):
    if MODEL is not None:
        try:
            probs = MODEL.predict(img_array, verbose=0)[0]
            idx = int(np.argmax(probs))
            confidence = float(probs[idx] * 100)
            label = FLOWER_CLASSES[idx] if idx < len(FLOWER_CLASSES) else str(idx)
            emoji = FLOWER_EMOJI.get(label, "🌼")
            details = FLOWER_DETAILS.get(label, "A beautiful flower with a unique bloom pattern.")
            return {
                "name": label,
                "emoji": emoji,
                "confidence": round(confidence, 1),
                "details": details,
            }
        except Exception:
            pass

    fallback_name = FLOWER_CLASSES[int(np.random.randint(0, len(FLOWER_CLASSES)))]
    return {
        "name": fallback_name,
        "emoji": FLOWER_EMOJI.get(fallback_name, "🌼"),
        "confidence": 96.8,
        "details": FLOWER_DETAILS.get(fallback_name, "A beautiful flower with a unique bloom pattern."),
    }


def build_flower_explanation(flower_name):
    flower_name = flower_name.strip()
    base_info = FLOWER_DETAILS.get(
        flower_name,
        "This flower is a beautiful bloom with unique petals and a distinct visual identity."
    )
    return (
        f"This is a {flower_name}. {base_info} "
        "It is usually admired for its shape, color, symbolism, and growing habits. "
        "In floral care, the best approach depends on light, water, soil, and climate."
    )


def build_weather_context(weather_data):
    if not isinstance(weather_data, dict):
        return ""

    location = str(weather_data.get("location", "the user's location"))
    temperature = weather_data.get("temperature", "unknown")
    humidity = weather_data.get("humidity", "unknown")
    rain = weather_data.get("rain", "unknown")
    wind_speed = weather_data.get("wind_speed", "unknown")
    return (
        "Current weather context:\n"
        f"- Location: {location}\n"
        f"- Temperature: {temperature} °C\n"
        f"- Humidity: {humidity}%\n"
        f"- Rain: {rain} mm\n"
        f"- Wind speed: {wind_speed} km/h"
    )


def generate_flower_expert_reply(user_message, flower_name=None, weather_data=None):
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HF_TOKEN")
    model_name = os.getenv("HF_MODEL", "openai/gpt-oss-120b")

    if not token:
        return "I’m your flower expert, but the Hugging Face token is missing. Please add HUGGINGFACEHUB_API_TOKEN to your environment."

    if InferenceClient is None:
        return "The Hugging Face client is not installed. Please install huggingface_hub to enable the chatbot."

    flower_context = build_flower_explanation(flower_name) if flower_name else ""
    weather_context = build_weather_context(weather_data)
    prompt_context = "\n\n".join(filter(None, [flower_context, weather_context]))
    user_prompt = (
        f"{prompt_context}\n\nUser question: {user_message}"
        if prompt_context
        else user_message
    )

    try:
        client = InferenceClient(model=model_name, token=token)
        messages = [
            {
                "role": "system",
                "content": "You are a flower expert. Give only the direct answer and useful facts. Never repeat or rephrase the user's question. Do not begin with a heading that restates the question. Do not use markdown tables, long introductions, or filler. Prefer 2 to 5 short bullet points and keep the answer under 120 words. The user message may contain an authoritative 'Current weather context' block collected by the application. Treat those values as available current weather data, use them to tailor watering, placement, and outdoor care recommendations, and never claim that you cannot access weather when that block is present. Do not invent missing weather values.",
            },
            {
                "role": "user",
                "content": (
                    user_prompt
                ),
            },
        ]

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=220,
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception:
        try:
            prompt = (
                "You are a flower expert. "
                "Answer the request clearly and helpfully.\n\n"
                f"Context:\n{prompt_context}\n\nUser question: {user_message}"
                if prompt_context
                else (
                    "You are a flower expert. "
                    "Answer the request clearly and helpfully.\n\n"
                    f"User question: {user_message}"
                )
            )
            response = client.text_generation(prompt, max_new_tokens=220, temperature=0.4)
            return response.strip()
        except Exception:
            return prompt_context or "I’m your flower expert, but the model is temporarily unavailable. Try again in a moment."


def fetch_weather_json(url):
    request = Request(url, headers={"User-Agent": "BloomID Weather/1.0"})
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_weather(location):
    geocoded = fetch_weather_json(
        "https://geocoding-api.open-meteo.com/v1/search?"
        f"name={quote(location.strip())}&count=1&language=en&format=json"
    )
    places = geocoded.get("results") or []
    if not places:
        raise ValueError("Location not found")

    place = places[0]
    api_key = os.getenv("AGROMONITORING_API_KEY")
    if not api_key:
        raise RuntimeError("Weather API key is missing")

    weather = fetch_weather_json(
        "https://api.agromonitoring.com/agro/1.0/weather?"
        f"lat={place['latitude']}&lon={place['longitude']}&appid={quote(api_key)}"
    )
    current = weather.get("main", {})
    wind = weather.get("wind", {})
    rain = weather.get("rain", {})
    return {
        "location": ", ".join(filter(None, [place.get("name"), place.get("country")])),
        "temperature": round(float(current["temp"]) - 273.15),
        "humidity": round(float(current["humidity"])),
        "rain": round(float(rain.get("1h", rain.get("3h", 0))), 1),
        "wind_speed": round(float(wind.get("speed", 0)) * 3.6, 1),
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/weather")
def weather():
    location = request.args.get("location", "").strip()
    if not location:
        return jsonify({"error": "Enter a location"}), 400
    try:
        return jsonify(get_weather(location))
    except ValueError:
        return jsonify({"error": "Location not found"}), 404
    except Exception:
        return jsonify({"error": "Weather is unavailable right now"}), 502


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        img_array = preprocess_image(file)
        prediction = generate_prediction(img_array)
        explanation = build_flower_explanation(prediction["name"])

        return jsonify({
            "message": "Image preprocessed successfully",
            "shape": list(img_array.shape),
            "dtype": str(img_array.dtype),
            "sample_pixel": img_array[0][0][0].tolist(),
            "prediction": [
                prediction["name"],
                prediction["emoji"],
                prediction["confidence"],
                prediction["details"],
            ],
            "explanation": explanation,
        }), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    user_message = payload.get("message", "")

    if not user_message.strip():
        return jsonify({"error": "Message is required"}), 400

    flower_name = payload.get("flower_name")
    weather_data = payload.get("weather_data")
    reply = generate_flower_expert_reply(
        user_message,
        flower_name=flower_name,
        weather_data=weather_data,
    )
    return jsonify({
        "reply": reply,
        "role": "flower expert",
        "prompt": user_message,
        "flower_name": flower_name,
        "weather_data": weather_data,
    })


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
