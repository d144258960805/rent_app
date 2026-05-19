from flask import Flask
import os
import sqlite3

def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secret_key_for_rent_app"
    
    # 註冊 Blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # 首頁路由導向至房源列表
    from flask import redirect, url_for
    @app.route('/')
    def index():
        return redirect(url_for('property_bp.index'))
        
    return app

def init_db():
    db_dir = os.path.join(os.getcwd(), 'instance')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'database.db')
    
    schema_path = os.path.join(os.getcwd(), 'database', 'schema.sql')
    if not os.path.exists(schema_path):
        print(f"錯誤: 找不到 schema 檔案 {schema_path}")
        return
        
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)
    conn.commit()
    conn.close()
    print("資料庫初始化完成！")
