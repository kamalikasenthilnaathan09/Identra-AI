from extensions import db

class KnowledgeNode(db.Model):
    __tablename__ = 'knowledge_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    node_type = db.Column(db.String(50), nullable=False) # Skill, Project, Certificate, Experience, Education, Internship
    properties = db.Column(db.Text, default='{}') # JSON string
    
    # Relationships for edges
    outgoing_edges = db.relationship('KnowledgeEdge', foreign_keys='KnowledgeEdge.source_id', backref='source_node', cascade="all, delete-orphan")
    incoming_edges = db.relationship('KnowledgeEdge', foreign_keys='KnowledgeEdge.target_id', backref='target_node', cascade="all, delete-orphan")

class KnowledgeEdge(db.Model):
    __tablename__ = 'knowledge_edges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('knowledge_nodes.id'), nullable=False)
    relation_type = db.Column(db.String(100), nullable=False) # Skill -> Project, Project -> Internship, Certificate -> Skill
