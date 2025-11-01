import os
import joblib


def load_models():
    """
    Loads trained ML models from 'saved_models' folder.
    Returns a dictionary of models.
    """
    base_path = os.path.join(os.path.dirname(__file__), "saved_models")
    models = {}

    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Model directory not found: {base_path}")

    for file in os.listdir(base_path):
        if file.endswith(".pkl"):
            name = file.replace(".pkl", "")
            with open(os.path.join(base_path, file), "rb") as f:
                models[name] = joblib.load(f)

    if not models:
        raise RuntimeError("No models found in saved_models folder.")

    print(f"✅ Models loaded: {list(models.keys())}")
    return models
