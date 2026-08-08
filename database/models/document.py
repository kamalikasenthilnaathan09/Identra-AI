from datetime import datetime
from extensions import db

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50), default='Others') # Personal Documents, Financial Documents, Transportation, Education, Certificates, Internship, Projects & Achievements, Resume & Career, Others
    subcategory = db.Column(db.String(100), default='General')
    status = db.Column(db.String(50), default='Completed') # Pending, Processing, Completed, Failed
    file_size = db.Column(db.Integer, nullable=False, default=0) # bytes
    extracted_text = db.Column(db.Text, nullable=True)
    ai_tags = db.Column(db.String(512), default='')
    file_path = db.Column(db.String(512), nullable=False)
    
    # AI Explanation & Dynamic Confidence Fields
    confidence_score = db.Column(db.Float, default=0.0) # E.g., 0.96 (96%)
    matched_keywords = db.Column(db.String(512), default='') # Comma separated matched phrases
    classification_reason = db.Column(db.Text, default='') # AI explanation for classification
    user_corrected = db.Column(db.Boolean, default=False) # True if manually corrected by user
    original_category = db.Column(db.String(100), nullable=True) # Pre-correction category
    corrected_category = db.Column(db.String(100), nullable=True) # User corrected category
    
    # Document Expiry & Renewal Tracking
    issue_date = db.Column(db.String(50), nullable=True)
    expiry_date = db.Column(db.String(50), nullable=True)
    renewal_date = db.Column(db.String(50), nullable=True)
    doc_number = db.Column(db.String(100), nullable=True)
    is_expiring_soon = db.Column(db.Boolean, default=False)
    
    # Relationship to embeddings
    embedding = db.relationship('DocumentEmbedding', backref='document', uselist=False, cascade="all, delete-orphan")
