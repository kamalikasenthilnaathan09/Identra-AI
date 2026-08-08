from extensions import db

class DocumentEmbedding(db.Model):
    __tablename__ = 'document_embeddings'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    vector_data = db.Column(db.Text, nullable=False) # JSON representation of floats list
