
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline

from extract_features import extract_features


# Update these paths for your downloaded dataset
AUDIO_DIR = Path("data/reading_confidence/audios")
CSV_PATH = Path("data/reading_confidence/ratings.csv")
MODEL_PATH = Path("backend/models/confidence_mlp.joblib")

df = pd.read_csv(CSV_PATH)

# Adapt these names to the actual CSV columns
AUDIO_COLUMN = "audio_filename"
LABEL_COLUMN = "confidence"

X = []
y = []

for _, row in df.iterrows():
    audio_path = AUDIO_DIR / str(row[AUDIO_COLUMN])
    label = str(row[LABEL_COLUMN]).strip().lower()

    if label not in {"low", "medium", "high"}:
        continue

    if not audio_path.exists():
        print(f"Missing audio: {audio_path}")
        continue

    try:
        X.append(extract_features(audio_path))
        y.append(label)
    except Exception as exc:
        print(f"Skipping {audio_path}: {exc}")

if len(X) < 10:
    raise ValueError("Not enough valid recordings to train.")

X = np.asarray(X)
y = np.asarray(y)

# Encode text labels as numeric classes
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# Hold out examples for evaluation
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

# Scale features, then train the MLP
model = Pipeline([
    ("scaler", StandardScaler()),
    ("mlp", MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation="relu",
        solver="adam",
        max_iter=500,
        early_stopping=True,
        random_state=42
    ))
])

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("Classes:", encoder.classes_)
print(classification_report(
    y_test,
    predictions,
    labels=np.arange(len(encoder.classes_)),
    target_names=encoder.classes_,
    zero_division=0
))
print("Confusion matrix:")
print(confusion_matrix(
    y_test,
    predictions,
    labels=np.arange(len(encoder.classes_))
))

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump({
    "model": model,
    "encoder": encoder,
    "feature_version": 1
}, MODEL_PATH)

print(f"Model saved to {MODEL_PATH}")
