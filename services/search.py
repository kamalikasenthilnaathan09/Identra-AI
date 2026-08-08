from database.models.document import Document
from database.models.graph import KnowledgeNode
from services.embeddings import generate_embedding, cosine_similarity

def search_user_identity(user_id, query_string):
    """
    Semantic Search engine combining Sentence Embedding similarity
    and multi-entity graph node filtering with match confidence scores.
    """
    query_string = query_string.strip()
    results = {
        'documents': [],
        'nodes': [],
        'query': query_string
    }
    
    if not query_string:
        return results
        
    query_lower = query_string.lower()
    
    # 1. Generate query embedding for vector semantic search
    query_vec_str = generate_embedding(query_string)
    
    # Fetch all user documents
    all_docs = Document.query.filter_by(user_id=user_id).all()
    scored_docs = []
    
    for doc in all_docs:
        # Calculate semantic cosine similarity
        sim_score = 0.0
        if doc.embedding:
            sim_score = cosine_similarity(query_vec_str, doc.embedding)
            
        # Keyword bonus boost if query terms appear in title or extracted text
        text_content = f"{doc.original_name} {doc.category} {doc.extracted_text or ''}".lower()
        if query_lower in text_content:
            sim_score += 0.35
            
        # Category match boost
        if 'certificate' in query_lower and doc.category == 'Certificate':
            sim_score += 0.3
        elif 'internship' in query_lower and doc.category == 'Internship':
            sim_score += 0.3
        elif 'resume' in query_lower and doc.category == 'Resume':
            sim_score += 0.3
        elif 'project' in query_lower and doc.category == 'Project':
            sim_score += 0.3
        elif 'academic' in query_lower and doc.category == 'Academic':
            sim_score += 0.3

        # Confidence percentage (bounded between 50% and 99%)
        confidence = min(99, max(50, int(sim_score * 100)))
        
        if sim_score > 0.05 or any(w in text_content for w in query_lower.split()):
            scored_docs.append((doc, confidence, sim_score))
            
    # Sort documents by score descending
    scored_docs.sort(key=lambda x: x[2], reverse=True)
    
    results['documents'] = [{
        'id': d[0].id,
        'original_name': d[0].original_name,
        'category': d[0].category,
        'upload_time': d[0].upload_time.strftime('%b %d, %Y'),
        'file_size': d[0].file_size,
        'status': d[0].status,
        'confidence': d[1],
        'extracted_text_snippet': (d[0].extracted_text[:180] + '...') if d[0].extracted_text else 'No text'
    } for d in scored_docs]

    # 2. Graph node match queries
    node_query = KnowledgeNode.query.filter_by(user_id=user_id)
    nodes = node_query.filter(
        (KnowledgeNode.label.ilike(f'%{query_string}%')) |
        (KnowledgeNode.node_type.ilike(f'%{query_string}%'))
    ).all()
    
    results['nodes'] = [{
        'id': n.id,
        'label': n.label,
        'node_type': n.node_type
    } for n in nodes]
    
    return results
