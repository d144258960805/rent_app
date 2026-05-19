from .user_routes import user_bp
from .property_routes import property_bp
from .review_routes import review_bp
from .roommate_routes import roommate_bp

def register_blueprints(app):
    """將所有 Blueprints 註冊至 Flask App"""
    app.register_blueprint(user_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(roommate_bp)
