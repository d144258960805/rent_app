import os
import sqlite3
from flask import Flask, render_template, g

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
    
    # ensure upload folder exists
    upload_path = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_path, exist_ok=True)
        
    # 註冊資料庫指令 (Our implementation)
    from . import db
    db.init_app(app)
    
    # 註冊 close_db teardown
    from .models import close_db
    app.teardown_appcontext(close_db)
    
    # 初始化資料庫 Schema
    def init_main_db():
        from .models import get_db as get_main_db
        main_db = get_main_db()
        schema_path = os.path.join(os.path.dirname(app.root_path), 'database', 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                main_db.cursor().executescript(f.read())
            main_db.commit()
        
        # 安全升級：確保 properties 表包含 image_path 欄位
        try:
            main_db.cursor().execute("ALTER TABLE properties ADD COLUMN image_path TEXT;")
            main_db.commit()
        except sqlite3.OperationalError:
            pass
        
        # 安全升級：確保 verifications 表包含額外欄位
        for col in ["owner_name", "property_address", "ai_report"]:
            try:
                main_db.cursor().execute(f"ALTER TABLE verifications ADD COLUMN {col} TEXT;")
                main_db.commit()
            except sqlite3.OperationalError:
                pass
        
        # 安全升級：更名 student_id 到 author_id
        try:
            main_db.cursor().execute("ALTER TABLE roommate_posts RENAME COLUMN student_id TO author_id;")
            main_db.commit()
        except sqlite3.OperationalError:
            pass
        
        # 安全升級：確保 roommate_posts 表包含新增欄位
        for col in ["room_type", "gender_preference", "lifestyle_rules"]:
            try:
                main_db.cursor().execute(f"ALTER TABLE roommate_posts ADD COLUMN {col} TEXT;")
                main_db.commit()
            except sqlite3.OperationalError:
                pass
    
    with app.app_context():
        try:
            init_main_db()
        except Exception:
            pass

    # 註冊 Blueprint 路由 (Our implementation)
    from .routes import property_routes
    app.register_blueprint(property_routes.bp)
    
    # 註冊核心 Blueprint (auth, property, roommate)
    from .routes import auth, property, roommate
    app.register_blueprint(auth.bp)
    app.register_blueprint(property.bp)
    app.register_blueprint(roommate.bp)
    
    # 初始化資料庫 (Other member's implementation)
    try:
        from app.models.listing import init_db as init_listing_db
        init_listing_db()
    except Exception:
        pass
        
    # 註冊 Blueprint (Other member's implementation)
    # 注意：listings_bp 的 '/' 路由會與首頁衝突且缺少模板，暫時停用
    # try:
    #     from app.routes.listings import listings_bp
    #     app.register_blueprint(listings_bp)
    # except Exception:
    #     pass
    
    # 首頁路由
    from flask import request as flask_request
    from .models.property import Property, Tag
    
    @app.route('/')
    def index():
        query = flask_request.args.get('query', '').strip()
        rent_range = flask_request.args.get('rent_range', '')
        room_type = flask_request.args.get('room_type', '')
        size_range = flask_request.args.get('size_range', '')
        subsidy_available = flask_request.args.get('subsidy_available', '')
        selected_tag = flask_request.args.get('tag', '')
        selected_tags = flask_request.args.getlist('tags')

        properties = Property.get_filtered(
            query=query,
            rent_range=rent_range,
            room_type=room_type,
            size_range=size_range,
            subsidy_available=subsidy_available,
            tag_name=selected_tag,
            tag_names=selected_tags if selected_tags else None
        )
        
        tags = Tag.get_all()
        grouped_tags, category_icons = Tag.get_grouped()
        return render_template(
            'index.html',
            properties=properties,
            tags=tags,
            grouped_tags=grouped_tags,
            category_icons=category_icons,
            query=query,
            rent_range=rent_range,
            room_type=room_type,
            size_range=size_range,
            subsidy_available=subsidy_available,
            selected_tag=selected_tag,
            selected_tags=selected_tags
        )
        
    return app
