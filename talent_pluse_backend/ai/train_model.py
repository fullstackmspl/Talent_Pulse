import os
import sys
import random
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

<<<<<<< HEAD
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
=======
# === TRAINING DATA ===
training_data = [
    # ─── GREETING ──────────────────────────────────────────────────────────────
    ("hi", "greeting")  , ("hello", "greeting"), ("hey", "greeting"),
    ("good morning", "greeting"), ("good afternoon", "greeting"), ("good evening", "greeting"),
    ("hi there", "greeting"), ("hello again", "greeting"), ("hey buddy", "greeting"),
    ("howdy", "greeting"), ("yo", "greeting"), ("hiya", "greeting"),
    ("morning", "greeting"), ("evening", "greeting"), ("greetings", "greeting"),
    ("hi bot", "greeting"), ("hello ai", "greeting"), ("hey there!", "greeting"),
    ("Good morning TalentPulse", "greeting"), ("sup", "greeting"),
    ("what's up", "greeting"), ("hey how are you", "greeting"),
>>>>>>> 2ad24486087246661a3f83edb66384685e74dd1b

from ai.text_preprocessing import normalize_query_text

from ai.training_data import EXPANDED_SAMPLES

random.seed(42)

TYPO_VARIANTS = {
    "what": ["wat", "wht"],
    "email": ["emial", "eamil", "mail"],
    "resume": ["resum", "rsume"],
    "document": ["documnt", "doc"],
    "uploaded": ["uploded", "uploadd"],
    "reliable": ["realiable", "relible"],
    "information": ["info", "infrmation"],
    "page": ["pg"],
    "summary": ["summry"],
    "summarize": ["sumarize", "summrize"],
    "technical": ["tecnical", "techincal"],
}

def typo_augment(text: str) -> list[str]:
    variants = {text}
    words = text.split()
    for i, word in enumerate(words):
        if word in TYPO_VARIANTS:
            for replacement in TYPO_VARIANTS[word]:
                candidate = words[:]
                candidate[i] = replacement
                variants.add(" ".join(candidate))
    return list(variants)

def expand_samples():
    expanded = []
    for text, label in EXPANDED_SAMPLES:
        # Augment with typos for better coverage
        for variant in typo_augment(normalize_query_text(text)):
            expanded.append((variant, label))
        expanded.append((normalize_query_text(text), label))
    return expanded


training_data = expand_samples()
texts = [text for text, _ in training_data]
labels = [label for _, label in training_data]

print(f"Total training samples after augmentation: {len(texts)}")

X_train, X_test, y_train, y_test = train_test_split(
    texts,
    labels,
    test_size=0.2,
    random_state=42,
    stratify=labels,
)

word_vectorizer = TfidfVectorizer(
    preprocessor=normalize_query_text,
    ngram_range=(1, 2),
    min_df=1,
    sublinear_tf=True,
)

char_vectorizer = TfidfVectorizer(
    preprocessor=normalize_query_text,
    analyzer="char_wb",
    ngram_range=(3, 5),
    min_df=1,
    sublinear_tf=True,
)

pipeline = Pipeline(
    [
        (
            "features",
            FeatureUnion(
                [
                    ("word", word_vectorizer),
                    ("char", char_vectorizer),
                ]
            ),
        ),
        (
            "clf",
            LogisticRegression(
                max_iter=4000,
                C=4.0,
                class_weight="balanced",
                solver="lbfgs",
            ),
        ),
    ]
)

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("=" * 70)
print("MODEL EVALUATION")
print("=" * 70)
print(f"Accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "model.pkl")
joblib.dump(pipeline, model_path)

print("\nModel saved successfully!")
print("Model path:", model_path)

test_queries = [
    "cannot login to dashboard",
    "wat is email of rahul in rahul_dhiman_resume.pdf",
    "sumarize this webpage https://example.com",
    "is this page reliable https://example.com",
    "add new lead for client",
    "show all candidates",
    "remind me tomorow morning",
]

print("\n" + "=" * 70)
print("SAMPLE PREDICTIONS")
print("=" * 70)
for query in test_queries:
    prediction = pipeline.predict([query])[0]
    probabilities = pipeline.predict_proba([query])[0]
    confidence = max(probabilities)
    print(f"\nUser Input : {query}")
    print(f"Predicted  : {prediction}")
    print(f"Confidence : {confidence:.2f}")
