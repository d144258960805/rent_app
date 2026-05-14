"""
app/__init__.py — Flask Application Factory
"""

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.secret_key = 'dev-secret-change-in-production'

    # 初始化資料庫
    from app.models.listing import init_db
    init_db()

    # 註冊 Blueprint
    from app.routes.listings import listings_bp
    app.register_blueprint(listings_bp)

    return app
