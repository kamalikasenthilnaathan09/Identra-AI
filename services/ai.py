from utils.document_classifier import classify_document_advanced

def classify_document(filename, text=""):
    """
    Wrapper function calling modular utils/document_classifier.py
    Returns main category name.
    """
    category, subcategory, ai_tags = classify_document_advanced(filename, text)
    return category
