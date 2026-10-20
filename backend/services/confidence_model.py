
from pathlib import Path
import joblib

from backend.training.extract_features import extract_features


MODEL_PATH = Path("backend/models/confidence_mlp.joblib")

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
encoder = bundle["encoder"]


def predict_vocal_delivery(audio_path):
    features = extract_features(audio_path).reshape(1, -1)

    probabilities = model.predict_proba(features)[0]
    best_index = probabilities.argmax()

    return {
        "predicted_level": str(encoder.classes_[best_index]),
        "class_probabilities": {
            str(label): round(float(prob), 4)
            for label, prob in zip(
                encoder.classes_, probabilities
            )
        }
    }
