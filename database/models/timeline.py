from datetime import datetime
from extensions import db

class TimelineEvent(db.Model):
    __tablename__ = 'timeline_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    event_type = db.Column(db.String(50), nullable=False) # Education, Project, Internship, Certificate
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
