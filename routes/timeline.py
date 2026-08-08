import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from extensions import db
from routes.auth import login_required
from database.models.timeline import TimelineEvent

timeline_bp = Blueprint('timeline', __name__)

def clean_text(text):
    if not text:
        return ""
    # Clean PDF font encoding artifacts like (cid:415) -> ti or remove
    text = re.sub(r'\(cid:\d+\)', '', text)
    return text.strip()

@timeline_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']
    events = TimelineEvent.query.filter_by(user_id=user_id).order_by(TimelineEvent.year.asc(), TimelineEvent.date_created.asc()).all()
    
    # Clean titles
    for e in events:
        if e.title:
            e.title = clean_text(e.title)
            
    return render_template('dashboard/timeline.html', events=events)

@timeline_bp.route('/add', methods=['POST'])
@login_required
def add():
    user_id = session['user_id']
    year = request.form.get('year')
    title = request.form.get('title')
    description = request.form.get('description')
    event_type = request.form.get('event_type') # Education, Project, Internship, Certificate
    
    if not year or not title or not event_type:
        flash('Year, Title, and Event Type are required.', 'danger')
        return redirect(url_for('timeline.index'))
        
    try:
        year_val = int(year)
    except ValueError:
        flash('Invalid year format.', 'danger')
        return redirect(url_for('timeline.index'))
        
    evt = TimelineEvent(
        user_id=user_id,
        year=year_val,
        title=clean_text(title),
        description=clean_text(description),
        event_type=event_type
    )
    db.session.add(evt)
    db.session.commit()
    
    flash('Timeline milestone added.', 'success')
    return redirect(url_for('timeline.index'))

@timeline_bp.route('/delete/<int:event_id>', methods=['POST', 'DELETE'])
@login_required
def delete(event_id):
    user_id = session['user_id']
    evt = TimelineEvent.query.filter_by(id=event_id, user_id=user_id).first_or_404()
    
    db.session.delete(evt)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method == 'DELETE':
        return jsonify({'success': True, 'message': 'Milestone deleted successfully'})
        
    flash('Timeline milestone deleted.', 'success')
    return redirect(url_for('timeline.index'))
