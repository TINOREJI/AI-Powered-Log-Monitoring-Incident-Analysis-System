import os

# Try loading ML dependencies safely
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    ML_AVAILABLE = True
except Exception as e:
    print(f"[ML WARNING] sentence-transformers not available: {e}")
    ML_AVAILABLE = False

# -------------------------
# Labels (important categories)
# -------------------------
labels = [
    "Security Alert",
    "System Error",
    "Resource Usage",
    "HTTP Activity",
    "System Activity",
    "Authentication Event",
    "Network Activity"
]

# -------------------------
# Lazy-loaded model
# -------------------------
model = None
label_embeddings = None


def load_model():
    global model, label_embeddings

    if not ML_AVAILABLE:
        return

    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        label_embeddings = model.encode(labels)


# -------------------------
# ML Classification (SAFE)
# -------------------------
def ml_classify(log_message: str, current_category: str):
    """
    Hybrid ML classifier:
    - Only overrides if current category is weak
    - Uses confidence threshold
    """

    if not ML_AVAILABLE:
        return current_category

    # Only apply ML for weak categories
    if current_category not in ["Other", "General Log"]:
        return current_category

    load_model()

    log_embedding = model.encode([log_message])
    scores = cosine_similarity(log_embedding, label_embeddings)[0]

    best_score = max(scores)
    best_label = labels[scores.argmax()]

    # 🔥 Confidence threshold
    if best_score >= 0.25:
        return best_label

    return current_category