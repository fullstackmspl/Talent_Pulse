import joblib
import os
import ai.text_preprocessing  # Ensures custom text normalizer is importable when loading the model.

# === UPDATED: INTENT PREDICTION SYSTEM ===
# The model is now a full sklearn Pipeline (TF-IDF + Classifier)
# so we don't need a separate vectorizer.pkl anymore.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# Singleton pattern for model loading
_model_pipeline = None

def load_model():
    global _model_pipeline
    if _model_pipeline is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Intent model file not found at {MODEL_PATH}. Please run training first.")
        _model_pipeline = joblib.load(MODEL_PATH)

def predict_intent(message: str) -> str:
    """
    Predicts the intent of a user message using the trained Pipeline.
    Expects raw text; the bundled TfidfVectorizer handles normalization.
    """
    load_model()
    # Pass as a list of strings [message] because the pipeline expects an iterable
    prediction = _model_pipeline.predict([message])[0]
    return prediction

def predict_intent_with_confidence(message: str):
    """
    Returns both the predicted intent and the confidence score.
    """
    load_model()
    probs = _model_pipeline.predict_proba([message])[0]
    best_intent_idx = probs.argmax()
    confidence = probs[best_intent_idx]
    intent = _model_pipeline.classes_[best_intent_idx]
    return intent, float(confidence)

# For backward compatibility
def detect_intent(message: str):
    return predict_intent(message)
