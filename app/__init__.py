from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from mongoengine import connect, disconnect
from datetime import datetime
from .config import get_settings
import logging

db = MongoEngine()
login_manager = LoginManager()
logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
    try:
        from .models import User
        return User.objects(id=user_id).first()
    except Exception as e:
        logger.error(f"Error loading user: {str(e)}")
        return None

def timeago_filter(value):
    """Convert a datetime string to a human-readable 'time ago' format."""
    try:
        dt = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S+0000')
        now = datetime.utcnow()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "just now"
    except Exception:
        return value

def create_app():
    # Disconnect any existing connections
    disconnect()
    
    app = Flask(__name__)
    settings = get_settings()
    
    # Configure MongoDB settings
    app.config['MONGODB_SETTINGS'] = {
        'db': settings.MONGODB_DB,
        'host': settings.MONGODB_HOST,
        'port': settings.MONGODB_PORT,
        'username': settings.MONGODB_USERNAME,
        'password': settings.MONGODB_PASSWORD
    }
    
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register Jinja2 filters BEFORE registering blueprints
    app.jinja_env.filters['timeago'] = timeago_filter
    
    # Register blueprints
    from .blueprints import (
        auth_bp, dashboard_bp, content_bp, 
        comments_bp, settings_bp, posts_bp,
        strategy_bp
    )
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(comments_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(strategy_bp)
    
    return app
