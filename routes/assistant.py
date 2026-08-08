from flask import Blueprint, render_template, request, jsonify, session
from extensions import db
from routes.auth import login_required
from database.models.chat import ChatHistory

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']
    history = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp.asc()).all()
    return render_template('dashboard/assistant.html', history=history)

@assistant_bp.route('/message', methods=['POST'])
@login_required
def message():
    user_id = session['user_id']
    data = request.get_json() or {}
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message content cannot be empty'}), 400
        
    # Save User message
    user_chat = ChatHistory(user_id=user_id, role='user', message=user_message)
    db.session.add(user_chat)
    db.session.commit()
    
    # Generate intelligent mock reply
    reply_text = get_assistant_response(user_message, user_id)
    
    # Save Assistant response
    assistant_chat = ChatHistory(user_id=user_id, role='assistant', message=reply_text)
    db.session.add(assistant_chat)
    db.session.commit()
    
    return jsonify({
        'reply': reply_text,
        'timestamp': assistant_chat.timestamp.strftime('%H:%M')
    })

def get_assistant_response(msg, user_id):
    msg_lower = msg.lower()
    
    if 'resume' in msg_lower or 'cv' in msg_lower:
        return "I detected your resume in your Identra database. It indicates education at Stanford University and skills like Python, Flask, React, and Machine Learning. Shall I help you update your timeline or connect these to a new project?"
    elif 'python' in msg_lower:
        return "You have strong Python alignments! I see it connected to your 'Smart Safety Network Project' and your 'Python Certified Professional' credential. Would you like me to map another skill node?"
    elif 'internship' in msg_lower or 'experience' in msg_lower:
        return "I see an AI Research Internship at NeuralTech (2026) listed. This matches skills in transformer models and machine learning. Let me know if you need to fetch the completion letter."
    elif 'certificate' in msg_lower or 'certification' in msg_lower:
        return "You currently have certifications including 'Python Certified Professional' (2024) and 'Deep Learning Course Specialization' (2025). I can scan another image if you upload it!"
    elif 'hello' in msg_lower or 'hi' in msg_lower or 'hey' in msg_lower:
        return "Hello! I am your Identra AI Assistant. I can index your career milestones, search certificates, structure knowledge graphs, or summarize recent resume uploads. What can I do for you today?"
        
    return f"I've processed your query: '{msg}'. I am searching your digital identity records. You can ask me questions like 'What are my Python projects?' or 'Find my internships' for direct semantic retrieval."
