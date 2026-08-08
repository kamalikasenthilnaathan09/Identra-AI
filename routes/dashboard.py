from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from extensions import db
from routes.auth import login_required
from database.models.user import User
from database.models.document import Document
from database.models.timeline import TimelineEvent
from database.models.graph import KnowledgeNode

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    
    # Dashboard summary statistics
    total_docs = Document.query.filter_by(user_id=user_id).count()
    certs = Document.query.filter_by(user_id=user_id, category='Certificate').count()
    internships = Document.query.filter_by(user_id=user_id, category='Internship').count()
    projects = Document.query.filter_by(user_id=user_id, category='Project').count()
    
    recent_uploads = Document.query.filter_by(user_id=user_id).order_by(Document.upload_time.desc()).limit(5).all()
    timeline_count = TimelineEvent.query.filter_by(user_id=user_id).count()
    node_count = KnowledgeNode.query.filter_by(user_id=user_id).count()
    
    # Calculate storage metrics (limit to 50MB for demo)
    used_bytes = db.session.query(db.func.sum(Document.file_size)).filter_by(user_id=user_id).scalar() or 0
    used_mb = round(used_bytes / (1024 * 1024), 2)
    storage_pct = min(100, int((used_mb / 50.0) * 100)) if used_mb > 0 else 0
    
    # Completion Score
    completion_score = 20  # Base score
    if total_docs > 0: completion_score += 20
    if certs > 0: completion_score += 15
    if internships > 0: completion_score += 15
    if projects > 0: completion_score += 15
    if timeline_count > 0: completion_score += 15
    completion_score = min(100, completion_score)

    return render_template('dashboard/index.html',
                           total_docs=total_docs,
                           certs=certs,
                           internships=internships,
                           projects=projects,
                           recent_uploads=recent_uploads,
                           timeline_count=timeline_count,
                           node_count=node_count,
                           storage_mb=used_mb,
                           storage_pct=storage_pct,
                           completion_score=completion_score)

@dashboard_bp.route('/graph')
@login_required
def graph():
    return render_template('dashboard/graph.html')

@dashboard_bp.route('/analytics')
@login_required
def analytics():
    return render_template('dashboard/analytics.html')

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        # Update user attributes
        new_email = request.form.get('email')
        if new_email and new_email.strip():
            existing_user = User.query.filter(User.email == new_email.strip(), User.id != user_id).first()
            if not existing_user:
                user.email = new_email.strip()

        user.full_name = request.form.get('full_name', user.full_name)
        user.phone = request.form.get('phone', user.phone)
        user.dob = request.form.get('dob', user.dob)
        user.gender = request.form.get('gender', user.gender)
        user.location = request.form.get('location', user.location)
        user.college = request.form.get('college', user.college)
        user.degree = request.form.get('degree', user.degree)
        user.department = request.form.get('department', user.department)
        user.graduation_year = int(request.form.get('graduation_year', user.graduation_year or 2026))
        user.bio = request.form.get('bio', user.bio)
        user.skills_list = request.form.get('skills_list', user.skills_list)
        
        user.social_github = request.form.get('social_github', user.social_github)
        user.social_linkedin = request.form.get('social_linkedin', user.social_linkedin)
        user.social_portfolio = request.form.get('social_portfolio', user.social_portfolio)
        user.social_leetcode = request.form.get('social_leetcode', user.social_leetcode)
        user.social_hackerrank = request.form.get('social_hackerrank', user.social_hackerrank)
        user.social_resume_website = request.form.get('social_resume_website', user.social_resume_website)
        
        db.session.commit()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Profile details committed to database'})
            
        flash('Profile details updated.', 'success')
        return redirect(url_for('dashboard.profile'))
        
    return render_template('dashboard/profile.html', user=user)

@dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.pref_dark_mode = 'pref_dark_mode' in request.form
        user.pref_notifications = 'pref_notifications' in request.form
        user.pref_language = request.form.get('pref_language', user.pref_language)
        user.pref_email_alerts = 'pref_email_alerts' in request.form
        user.pref_auto_ai_scan = 'pref_auto_ai_scan' in request.form
        user.pref_ocr_on_upload = 'pref_ocr_on_upload' in request.form
        user.pref_default_category = request.form.get('pref_default_category', user.pref_default_category)
        user.pref_theme_preset = request.form.get('pref_theme_preset', user.pref_theme_preset or 'default')
        
        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        if current_pw and new_pw:
            if user.check_password(current_pw):
                user.set_password(new_pw)
                flash('Password updated successfully.', 'success')
            else:
                flash('Current password verification failed.', 'danger')
        else:
            flash('System configuration updated successfully.', 'success')
            
        db.session.commit()
        return redirect(url_for('dashboard.settings'))
        
    return render_template('dashboard/settings.html', user=user)

@dashboard_bp.route('/resume-builder')
@login_required
def resume_builder():
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    events = TimelineEvent.query.filter_by(user_id=user_id).order_by(TimelineEvent.year.desc()).all()
    
    education = [e for e in events if e.event_type == 'Education']
    experience = [e for e in events if e.event_type == 'Internship']
    projects = [e for e in events if e.event_type == 'Project']
    certificates = [e for e in events if e.event_type == 'Certificate']
    skills = user.skills_list.split(',') if user.skills_list else []
    
    return render_template('dashboard/resume_builder.html', 
                           user=user, 
                           education=education, 
                           experience=experience, 
                           projects=projects, 
                           certificates=certificates, 
                           skills=skills)


