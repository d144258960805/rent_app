from flask import Flask
import os
import sqlite3

def create_app():
    app = Flask(__name__)
    app.secret_key = "super_secret_key_for_rent_app"
    
    # 自動初始化資料庫與測試資料
    db_path = os.path.join(os.getcwd(), 'instance', 'database.db')
    if not os.path.exists(db_path):
        print("偵測到資料庫不存在，啟動初始化與種子資料建置...")
        init_db()
    
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
    
    # ================= 種子資料 (Seeding) =================
    print("正在寫入 Web 版初始測試資料...")
    
    # 1. 插入使用者
    users = [
        # (role, email, password_hash, name, phone, points, is_verified, created_at)
        ('landlord', 'landlord@fcu.edu.tw', '123456', '張房東', '0912345678', 100, 1, '2026-05-21 12:00:00'),
        ('student', 'student@fcu.edu.tw', '123456', '李同學', '0987654321', 100, 1, '2026-05-21 12:00:00')
    ]
    cursor.executemany('''
        INSERT INTO users (role, email, password_hash, name, phone, points, is_verified, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', users)
    
    # 2. 插入房源
    properties = [
        # (landlord_id, title, description, address, price, room_type, size, has_subsidy, created_at, updated_at)
        (1, "逢甲大學旁優質套房", "離學校超近的極致套房，生活便利！", "西屯區文華路100號", 6500, "獨立套房", 7.5, 0, '2026-05-21 12:00:00', '2026-05-21 12:00:00'),
        (1, "精緻採光陽台大套房 (可租補)", "全新落成大陽台套房，採光極佳，生活品質優！", "西屯區福星路50號", 8000, "獨立套房", 9.0, 1, '2026-05-21 12:00:00', '2026-05-21 12:00:00'),
        (1, "溫馨寵物友善公寓 (垃圾免追)", "可開伙、可養寵物，免仲介費的好租處。", "西屯區逢甲路20號", 5500, "分租套房", 6.0, 0, '2026-05-21 12:00:00', '2026-05-21 12:00:00'),
        (1, "文華商圈電梯套房附車位", "電梯大樓，含垃圾集中代收與專屬車位，學生最愛！", "西屯區西安街10號", 7000, "獨立套房", 8.0, 0, '2026-05-21 12:00:00', '2026-05-21 12:00:00'),
        (1, "奢華高樓落地窗景觀家庭房", "乾濕分離、台水台電大空間，附落地窗及獨立陽台。", "西屯區河南路二段", 15000, "整層住家", 22.0, 1, '2026-05-21 12:00:00', '2026-05-21 12:00:00')
    ]
    cursor.executemany('''
        INSERT INTO properties (landlord_id, title, description, address, price, room_type, size, has_subsidy, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', properties)
    
    # 3. 插入標籤
    tags = [
        # 房源 1
        (1, "離校區5分內"), (1, "台水台電"), (1, "有外窗"), (1, "獨立洗衣機"), (1, "免仲介費"),
        # 房源 2
        (2, "獨立陽台"), (2, "採光好"), (2, "乾濕分離"), (2, "近捷運"), (2, "可申請租補"), (2, "電梯大樓"),
        # 房源 3
        (3, "養寵物"), (3, "垃圾代收"), (3, "非頂加"), (3, "免仲介費"), (3, "子母車"),
        # 房源 4
        (4, "電梯大樓"), (4, "垃圾代收"), (4, "有小客車/機車位"), (4, "離校區5分內"), (4, "有外窗"),
        # 房源 5
        (5, "乾濕分離"), (5, "台水台電"), (5, "獨立陽台"), (5, "落地窗"), (5, "電梯大樓"), (5, "有小客車/機車位"), (5, "垃圾代收")
    ]
    cursor.executemany('''
        INSERT INTO property_tags (property_id, tag_name)
        VALUES (?, ?)
    ''', tags)
    
    # 4. 插入室友徵求文
    roommate_posts = [
        (2, "文華路分租套房徵室友！", "希望能找愛乾淨的逢甲同學，平常不抽菸不打麻將，作息正常。", '不限', '2026-05-21 12:00:00')
    ]
    cursor.executemany('''
        INSERT INTO roommate_posts (student_id, title, content, required_gender, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', roommate_posts)
    
    # 5. 插入評論
    reviews = [
        (1, 2, "這間套房採光真的很棒，隔音也算及格，離逢甲正門走路不到5分鐘，大推！", None, '2026-05-21 12:00:00')
    ]
    cursor.executemany('''
        INSERT INTO reviews (property_id, student_id, content, image_url, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', reviews)
    
    conn.commit()
    conn.close()
    print("資料庫與完整種子資料建置完成！")
