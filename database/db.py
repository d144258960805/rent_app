import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rent_app.db")

def get_db_connection():
    """取得 SQLite 資料庫連線"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_connection():
    """取得 SQLite 資料庫連線 (相容格式)"""
    return get_db_connection()

def init_db():
    """初始化資料庫表格"""
    # 確保資料庫目錄存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. 建立 users 表格 (使用者資訊)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            credit_score INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. 建立 properties 表格 (房源資訊)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            landlord_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            rent INTEGER NOT NULL,
            room_type TEXT NOT NULL,
            size REAL,
            has_subsidy BOOLEAN DEFAULT 0,
            tags TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (landlord_id) REFERENCES users (id)
        )
    ''')

    # 3. 建立 reviews 表格 (評論與照片)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            image_url TEXT,
            is_anonymous BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (property_id) REFERENCES properties (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 4. 建立 credits 表格 (信用積分變更紀錄)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_user_id INTEGER NOT NULL,
            reviewer_id INTEGER NOT NULL,
            score_change INTEGER NOT NULL,
            reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_user_id) REFERENCES users (id),
            FOREIGN KEY (reviewer_id) REFERENCES users (id)
        )
    ''')

    # 5. 建立 roommates 表格 (揪團找室友區)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roommates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            expected_rent INTEGER,
            room_type TEXT,
            gender_preference TEXT,
            lifestyle_rules TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 升級現有資料表結構以支援新期望條件欄位
    for col in ["room_type", "gender_preference", "lifestyle_rules"]:
        try:
            cursor.execute(f"ALTER TABLE roommates ADD COLUMN {col} TEXT;")
        except sqlite3.OperationalError:
            pass
    
    # 6. 建立 credit_logs 表格
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            points INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 7. 建立標籤關聯表 (與其他模組相容)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS property_tags (
            property_id INTEGER NOT NULL,
            tag_name TEXT NOT NULL,
            PRIMARY KEY (property_id, tag_name),
            FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print(f"資料庫初始化完成！已建立或確認表格存在。資料庫位置：{DB_PATH}")

def insert_dummy_data():
    """插入測試資料"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先清空資料避免重複
    cursor.execute("DELETE FROM property_tags")
    cursor.execute("DELETE FROM properties")
    
    # 插入測試房源
    properties = [
        ("逢甲大學旁優質套房", 6500, "西屯區文華路100號", "獨立套房"),
        ("全新採光大陽台套房", 8000, "西屯區福星路50號", "獨立套房"),
        ("溫馨可養寵物小套房", 5500, "西屯區逢甲路20號", "分租套房"),
        ("近商圈生活機能佳套房", 7000, "西屯區西安街10號", "獨立套房"),
        ("高級乾濕分離家庭房", 15000, "西屯區河南路二段", "整層住家")
    ]
    
    for p in properties:
        cursor.execute('''
            INSERT INTO properties (title, rent, address, room_type)
            VALUES (?, ?, ?, ?)
        ''', p)
    
    conn.commit()
    
    # 獲取剛插入的房源 ID
    cursor.execute("SELECT id FROM properties ORDER BY id ASC")
    p_ids = [row[0] for row in cursor.fetchall()]
    
    if len(p_ids) >= 5:
        tags = [
            (p_ids[0], "離校區5分內"), (p_ids[0], "台水台電"), (p_ids[0], "有外窗"), (p_ids[0], "獨立洗衣機"), (p_ids[0], "免仲介費"),
            (p_ids[1], "獨立陽台"), (p_ids[1], "採光好"), (p_ids[1], "乾濕分離"), (p_ids[1], "近捷運"), (p_ids[1], "可申請租補"), (p_ids[1], "電梯大樓"),
            (p_ids[2], "養寵物"), (p_ids[2], "垃圾代收"), (p_ids[2], "非頂加"), (p_ids[2], "免仲介費"), (p_ids[2], "子母車"),
            (p_ids[3], "電梯大樓"), (p_ids[3], "垃圾代收"), (p_ids[3], "有小客車/機車位"), (p_ids[3], "離校區5分內"), (p_ids[3], "有外窗"),
            (p_ids[4], "乾濕分離"), (p_ids[4], "台水台電"), (p_ids[4], "獨立陽台"), (p_ids[4], "落地窗"), (p_ids[4], "電梯大樓"), (p_ids[4], "有小客車/機車位"), (p_ids[4], "垃圾代收")
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO property_tags (property_id, tag_name)
            VALUES (?, ?)
        ''', tags)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    insert_dummy_data()
    print("資料庫與測試資料已建立完成！")
