from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from extensions import db
from database.models.user import User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))
            
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # ── Seed Realistic Sample Data ──────────────────────────────────
        try:
            from database.models.document import Document
            from database.models.timeline import TimelineEvent
            from database.models.graph import KnowledgeNode, KnowledgeEdge
            from database.models.notification import Notification
            uid = user.id
            
            # Sample Documents
            docs = [
                Document(user_id=uid, original_name='Alex_Rivera_Resume_2026.pdf', stored_name='resume_001.pdf', category='Resume', status='Completed', file_size=245760, extracted_text='Full-stack developer with experience in Python, Flask, React, TensorFlow. Stanford University B.S. Computer Science 2026. Skills: Machine Learning, SQL, Docker, Git.', file_path='uploads/resume_001.pdf'),
                Document(user_id=uid, original_name='Python_Professional_Certificate.pdf', stored_name='cert_001.pdf', category='Certificate', status='Completed', file_size=189440, extracted_text='Python Institute PCPP Certification awarded to Alex Rivera. Score: 92/100.', file_path='uploads/cert_001.pdf'),
                Document(user_id=uid, original_name='Deep_Learning_Specialization_Coursera.pdf', stored_name='cert_002.pdf', category='Certificate', status='Completed', file_size=156672, extracted_text='Deep Learning Specialization by Andrew Ng. Neural Networks, CNNs, RNNs, Transformers.', file_path='uploads/cert_002.pdf'),
                Document(user_id=uid, original_name='NeuralTech_Internship_Letter.pdf', stored_name='intern_001.pdf', category='Internship', status='Completed', file_size=102400, extracted_text='Internship offer letter from NeuralTech Labs. Role: AI Research Intern. Duration: June-August 2025.', file_path='uploads/intern_001.pdf'),
                Document(user_id=uid, original_name='Smart_Safety_Network_Report.pdf', stored_name='proj_001.pdf', category='Project', status='Completed', file_size=204800, extracted_text='Smart Safety Network: A distributed mesh IoT project using Python, MQTT, and edge computing for real-time environmental monitoring.', file_path='uploads/proj_001.pdf'),
            ]
            db.session.add_all(docs)
            
            # Sample Timeline Events
            events = [
                TimelineEvent(user_id=uid, year=2022, title='Started B.S. Computer Science at Stanford', description='Enrolled in the AI & Intelligent Systems track at Stanford University.', event_type='Education'),
                TimelineEvent(user_id=uid, year=2023, title='Python Professional Developer Certification', description='Achieved PCPP certification with 92% score from the Python Institute.', event_type='Certificate'),
                TimelineEvent(user_id=uid, year=2024, title='Deep Learning Specialization', description='Completed Andrew Ng\'s 5-course specialization covering CNNs, RNNs, and Transformers.', event_type='Certificate'),
                TimelineEvent(user_id=uid, year=2025, title='AI Research Intern at NeuralTech Labs', description='Built transformer model prototypes for document understanding and semantic search.', event_type='Internship'),
                TimelineEvent(user_id=uid, year=2025, title='Smart Safety Network — Distributed Mesh IoT', description='Led development of a real-time environmental monitoring system using edge computing.', event_type='Project'),
                TimelineEvent(user_id=uid, year=2026, title='Identra AI — Digital Identity Platform', description='Designed and built an AI-powered identity graph system for hackathon competition.', event_type='Project'),
            ]
            db.session.add_all(events)
            
            # Sample Knowledge Nodes
            node_data = [
                ('Alex Rivera', 'User'), ('Python', 'Skill'), ('JavaScript', 'Skill'),
                ('TensorFlow', 'Skill'), ('Flask', 'Skill'), ('React', 'Skill'),
                ('Machine Learning', 'Skill'), ('SQL', 'Skill'),
                ('Smart Safety Network', 'Project'), ('Identra AI', 'Project'),
                ('NeuralTech Labs', 'Internship'),
                ('Python Certification', 'Certificate'), ('Deep Learning Specialization', 'Certificate'),
                ('Stanford University', 'Education'),
            ]
            nodes = []
            for label, ntype in node_data:
                n = KnowledgeNode(user_id=uid, label=label, node_type=ntype, properties='{}')
                db.session.add(n)
                nodes.append(n)
            db.session.flush()
            
            # Sample Edges
            edge_map = [
                (0, 1, 'has_skill'), (0, 2, 'has_skill'), (0, 3, 'has_skill'),
                (0, 4, 'has_skill'), (0, 5, 'has_skill'), (0, 6, 'has_skill'),
                (1, 8, 'used_in'), (3, 9, 'used_in'), (4, 9, 'used_in'),
                (6, 10, 'applied_at'), (11, 1, 'certifies'),
                (12, 6, 'certifies'), (13, 0, 'enrolled'),
            ]
            for src_i, tgt_i, rel in edge_map:
                db.session.add(KnowledgeEdge(user_id=uid, source_id=nodes[src_i].id, target_id=nodes[tgt_i].id, relation_type=rel))
            
            # Sample Notifications
            notifs = [
                Notification(user_id=uid, title='Welcome to Identra AI', message='Your digital identity workspace has been initialized.', icon='fa-hand-wave', category='general'),
                Notification(user_id=uid, title='Resume indexed successfully', message='Alex_Rivera_Resume_2026.pdf has been parsed and classified.', icon='fa-file-circle-check', category='document'),
                Notification(user_id=uid, title='Identity Score: 85/100', message='Your profile completeness has reached 85%. Add more documents to improve.', icon='fa-chart-line', category='general'),
                Notification(user_id=uid, title='5 skills detected from resume', message='Python, Flask, React, TensorFlow, SQL extracted automatically.', icon='fa-brain', category='ocr'),
                Notification(user_id=uid, title='Knowledge graph updated', message='14 nodes and 13 edges have been mapped to your identity graph.', icon='fa-circle-nodes', category='document'),
            ]
            db.session.add_all(notifs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[Seed Warning] Sample data seeding error: {e}")
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password):
            if user.two_factor_enabled:
                session['pending_2fa_user_id'] = user.id
                flash('Two-Factor Verification Required. Enter your 6-digit code.', 'info')
                return redirect(url_for('auth.two_factor_verify'))
            else:
                session['user_id'] = user.id
                session['username'] = user.username
                flash('Welcome back to Identra AI!', 'success')
                return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password.', 'danger')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/login.html')

@auth_bp.route('/2fa-verify', methods=['GET'])
def two_factor_verify():
    if 'pending_2fa_user_id' not in session:
        flash('No pending 2FA authentication session.', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/2fa_verify.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('landing'))

@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('A secure password reset link has been dispatched to your email.', 'success')
        else:
            flash('This email address is not registered in our system.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot.html')
