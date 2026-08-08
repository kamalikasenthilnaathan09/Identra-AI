import os
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from extensions import db, bcrypt, migrate
import database.models

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.documents import documents_bp
from routes.timeline import timeline_bp
from routes.search import search_bp
from routes.assistant import assistant_bp
from routes.api import api_bp
from routes.google_drive import google_drive_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(timeline_bp, url_prefix='/timeline')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(assistant_bp, url_prefix='/assistant')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(google_drive_bp, url_prefix='/google-drive')
    
    # Root Landing routes
    @app.route('/')
    @app.route('/landing')
    @app.route('/landing/')
    def landing():
        return render_template('landing.html')
        
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # About page
    @app.route('/about')
    def about():
        return render_template('about.html')
        
    # Context Processor for common variables (like username, total upload count, etc. in dashboard layout)
    @app.context_processor
    def inject_user_info():
        from services.i18n import get_translations
        user_info = {'dark_mode': True, 'theme_preset': 'default', 'notifications_enabled': True, 'language': 'English'}
        if 'user_id' in session:
            user_info['username'] = session.get('username')
            try:
                from database.models.user import User
                from database.models.document import Document
                user = User.query.get(session['user_id'])
                if user:
                    user_info['dark_mode'] = user.pref_dark_mode if user.pref_dark_mode is not None else True
                    user_info['theme_preset'] = user.pref_theme_preset or 'default'
                    user_info['notifications_enabled'] = user.pref_notifications if user.pref_notifications is not None else True
                    user_info['language'] = user.pref_language or 'English'

                used_bytes = db.session.query(db.func.sum(Document.file_size)).filter_by(user_id=session['user_id']).scalar() or 0
                used_mb = round(used_bytes / (1024 * 1024), 2)
                storage_pct = min(100, int((used_mb / 50.0) * 100)) if used_mb > 0 else 0
                user_info['storage_mb'] = used_mb
                user_info['storage_pct'] = storage_pct
            except Exception:
                user_info['storage_mb'] = 0
                user_info['storage_pct'] = 0

        t = get_translations(user_info.get('language', 'English'))
        return dict(user_info=user_info, query='', t=t)
        
    # Initialize DB (run once or in shell)
    with app.app_context():
        os.makedirs(os.path.join(app.config['BASE_DIR'], 'instance'), exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        db.create_all()
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
