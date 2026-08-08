from flask import Blueprint, render_template, request, session
from routes.auth import login_required
from services.search import search_user_identity

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']
    query = request.args.get('q', '')
    results = None
    
    if query:
        results = search_user_identity(user_id, query)
        
    return render_template('dashboard/search.html', query=query, results=results)
