import json
from database.models.graph import KnowledgeNode, KnowledgeEdge

def update_knowledge_graph(user_id, parsed_data, db):
    """
    Constructs nodes and relationships (edges) based on parsed document details.
    """
    skills = parsed_data.get('skills', [])
    projects = parsed_data.get('projects', [])
    experience = parsed_data.get('experience', [])
    education = parsed_data.get('education', [])
    certifications = parsed_data.get('certifications', [])
    
    def get_or_create_node(label, node_type):
        # Normalize labels to fit graph nicely
        clean_label = label.strip()
        if len(clean_label) > 40:
            # Try to grab title or shorten
            clean_label = clean_label.split('-')[0].split(':')[0].strip()[:37] + "..."
        
        node = KnowledgeNode.query.filter_by(user_id=user_id, label=clean_label, node_type=node_type).first()
        if not node:
            node = KnowledgeNode(user_id=user_id, label=clean_label, node_type=node_type, properties='{}')
            db.session.add(node)
            db.session.flush() # resolve ID
        return node

    # Create nodes
    skill_nodes = [get_or_create_node(s, 'Skill') for s in skills if s.strip()]
    proj_nodes = [get_or_create_node(p, 'Project') for p in projects if p.strip()]
    cert_nodes = [get_or_create_node(c, 'Certificate') for c in certifications if c.strip()]
    exp_nodes = [get_or_create_node(e, 'Internship') for e in experience if e.strip()]
    edu_nodes = [get_or_create_node(edu, 'Education') for edu in education if edu.strip()]

    # Relational connection heuristics:
    # 1. Certificate -> Skill
    for c_node in cert_nodes:
        for s_node in skill_nodes:
            if s_node.label.lower() in c_node.label.lower() or any(w in c_node.label.lower() for w in s_node.label.lower().split()):
                create_edge(user_id, c_node.id, s_node.id, 'Certificate -> Skill', db)
                
    # 2. Skill -> Project
    for p_node in proj_nodes:
        for s_node in skill_nodes:
            create_edge(user_id, s_node.id, p_node.id, 'Skill -> Project', db)

    # 3. Project -> Internship
    for p_node in proj_nodes:
        for e_node in exp_nodes:
            create_edge(user_id, p_node.id, e_node.id, 'Project -> Internship', db)
            
    # 4. Education -> Skill (general bridge)
    for edu_node in edu_nodes:
        for s_node in skill_nodes[:2]: # limit complexity
            create_edge(user_id, edu_node.id, s_node.id, 'Education -> Skill', db)

    db.session.commit()

def create_edge(user_id, source_id, target_id, relation_type, db):
    if source_id == target_id:
        return
    existing = KnowledgeEdge.query.filter_by(
        user_id=user_id,
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type
    ).first()
    
    if not existing:
        edge = KnowledgeEdge(
            user_id=user_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type
        )
        db.session.add(edge)
        db.session.flush()
