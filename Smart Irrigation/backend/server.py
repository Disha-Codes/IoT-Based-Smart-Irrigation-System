from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)
# Get current file directory (backend folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load trained models
model_water = joblib.load(os.path.join(BASE_DIR, "../models/water_model.pkl"))
model_duration = joblib.load(os.path.join(BASE_DIR, "../models/duration_model.pkl"))

# ---------------- ENCODING MAPS ----------------
crop_map = {
    "Chilli": 0,
    "Carrot": 1
}

stage_map = {
    "Germination": 0,
    "Vegetative": 1,
    "Flowering": 2,
    "Fruiting": 3
}

# ---------------- ROUTE ----------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json

        # Extract values
        soil = data['soil']
        temp = data['temp']
        hum = data['humidity']
        crop = data['crop']
        stage = data['stage']

        # Encode categorical values
        crop_encoded = crop_map.get(crop, 0)
        stage_encoded = stage_map.get(stage, 0)

        # Prepare input for ML model
        input_data = np.array([[soil, temp, hum, crop_encoded, stage_encoded]])

        # Predictions
        water = model_water.predict(input_data)[0]
        duration = model_duration.predict(input_data)[0]

        return jsonify({
            "water": int(water),
            "duration": int(duration)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route('/')
def home():
    return "AI Irrigation Server Running 🚀"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

