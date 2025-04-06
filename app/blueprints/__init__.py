from .auth import auth_bp
from .dashboard import dashboard_bp
from .content import content_bp
from .comments import comments_bp
from .settings import settings_bp
from .posts import posts_bp
from .strategy import strategy_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'content_bp',
    'comments_bp',
    'settings_bp',
    'posts_bp',
    'strategy_bp'
]

def register_blueprints(app):
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(posts_bp)  # Remove url_prefix as it's defined in the blueprint
    app.register_blueprint(comments_bp)
    app.register_blueprint(strategy_bp)
    # Register other blueprints
