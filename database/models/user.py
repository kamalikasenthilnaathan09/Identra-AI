from datetime import datetime
from extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Profile Information
    full_name = db.Column(db.String(100), default='Alex Rivera')
    phone = db.Column(db.String(20), default='+1 (555) 839-2091')
    dob = db.Column(db.String(20), default='2002-04-12')
    gender = db.Column(db.String(20), default='Male')
    location = db.Column(db.String(100), default='San Francisco, CA')
    college = db.Column(db.String(200), default='Stanford University')
    degree = db.Column(db.String(100), default='B.S. in Computer Science')
    department = db.Column(db.String(100), default='AI & Intelligent Systems')
    graduation_year = db.Column(db.Integer, default=2026)
    bio = db.Column(db.Text, default='AI enthusiast, full-stack engineer, and developer working on dynamic digital identities and neural networks.')
    
    # Skills List (stored as a comma-separated string)
    skills_list = db.Column(db.Text, default='Python,JavaScript,Machine Learning,TensorFlow,SQL,Flask,React')
    
    # Social Links
    social_github = db.Column(db.String(200), default='https://github.com/alexrivera')
    social_linkedin = db.Column(db.String(200), default='https://linkedin.com/in/alexrivera')
    social_portfolio = db.Column(db.String(200), default='https://alexrivera.dev')
    social_leetcode = db.Column(db.String(200), default='https://leetcode.com/alexrivera')
    social_hackerrank = db.Column(db.String(200), default='https://hackerrank.com/alexrivera')
    social_resume_website = db.Column(db.String(200), default='https://alexresume.dev')
    
    # Preferences
    pref_dark_mode = db.Column(db.Boolean, default=True)
    pref_notifications = db.Column(db.Boolean, default=True)
    pref_language = db.Column(db.String(30), default='English')
    pref_email_alerts = db.Column(db.Boolean, default=True)
    pref_auto_ai_scan = db.Column(db.Boolean, default=True)
    pref_ocr_on_upload = db.Column(db.Boolean, default=True)
    pref_default_category = db.Column(db.String(50), default='Other')
    pref_theme_preset = db.Column(db.String(50), default='default')
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(100), nullable=True)
    personal_vault_passkey = db.Column(db.String(256), nullable=True, default='1234')
    is_personal_vault_locked = db.Column(db.Boolean, default=True)
    
    # Relationships
    documents = db.relationship('Document', backref='owner', lazy=True, cascade="all, delete-orphan")
    timeline_events = db.relationship('TimelineEvent', backref='user', lazy=True, cascade="all, delete-orphan")
    nodes = db.relationship('KnowledgeNode', backref='user', lazy=True, cascade="all, delete-orphan")
    edges = db.relationship('KnowledgeEdge', backref='user', lazy=True, cascade="all, delete-orphan")
    chat_history = db.relationship('ChatHistory', backref='user', lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
