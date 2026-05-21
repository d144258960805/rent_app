import os
from flask import Flask

def create_app():
    # 建立 Flask 應用程式實例
    app = Flask(__name__, instance_relative_config=True)
    
    # 基本設定
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-change-in-production'),
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )
    
    # 確保 instance 資料夾存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # 註冊資料庫指令 (Our implementation)
    from . import db
    db.init_app(app)

    # 註冊 Blueprint 路由 (Our implementation)
    from .routes import property_routes
    app.register_blueprint(property_routes.bp)
    
    # 初始化資料庫 (Other member's implementation)
    try:
        from app.models.listing import init_db as init_listing_db
        init_listing_db()
    except Exception:
        pass
        
    # 註冊 Blueprint (Other member's implementation)
    try:
        from app.routes.listings import listings_bp
        app.register_blueprint(listings_bp)
    except Exception:
        pass
    
    # 首頁路由 (暫時導向房源清單)
    from flask import redirect, url_for
    @app.route('/')
    def index():
        return redirect('/properties')
        
    return app
