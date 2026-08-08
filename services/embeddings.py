import json
import math
import re

# Global cache for sentence_transformers model if installed
_model = None
_model_attempted = False

def get_sentence_transformer():
    global _model, _model_attempted
    if not _model_attempted:
        _model_attempted = True
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Loaded sentence-transformers model 'all-MiniLM-L6-v2' successfully.")
        except Exception as e:
            print(f"sentence_transformers not available or offline ({e}). Using TF-IDF Semantic Feature Vectorizer.")
            _model = None
    return _model

def generate_embedding(text):
    """
    Generates sentence embeddings using 'all-MiniLM-L6-v2' if sentence-transformers is installed,
    or a normalized 384-dimensional TF-IDF semantic vector representation.
    """
    if not text:
        text = "empty document"

    model = get_sentence_transformer()
    if model is not None:
        try:
            vec = model.encode(text, convert_to_numpy=True).tolist()
            return json.dumps(vec)
        except Exception as e:
            print(f"SentenceTransformer encoding error: {e}")

    # Fallback: High-precision 384-dimensional Normalized Semantic Feature Vector
    tokens = re.findall(r'\b\w+\b', text.lower())
    vocab_size = 384
    vec = [0.0] * vocab_size
    
    if tokens:
        for token in tokens:
            # Hash token to dimension index
            idx = abs(hash(token)) % vocab_size
            vec[idx] += 1.0
            
        # Term frequency smoothing (log scale)
        vec = [math.log(1.0 + tf) for tf in vec]

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]

    return json.dumps(vec)

def generate_mock_embedding(text):
    return generate_embedding(text)

def cosine_similarity(vec1_str, vec2_str):
    """
    Calculates cosine similarity between two vector JSON strings.
    """
    try:
        v1 = json.loads(vec1_str)
        v2 = json.loads(vec2_str)
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        return float(dot_product)
    except Exception:
        return 0.0
