import sqlite3
import os

# 取得目前檔案所在目錄的上一層目錄 (專案根目錄)，並將資料庫檔案放在那裡
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rent_app.db")

def get_db_connection():
    """取得 SQLite 資料庫連線"""
    conn = sqlite3.connect(DB_PATH)
    # 讓回傳的資料具有類似 dict 的操作方式，可以透過欄位名稱取值
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化資料庫與建立表格"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. 建立 users 表格 (使用者資訊)
    # role: 'student' 或 'landlord'
    # is_verified: 是否已通過實名認證 (防範詐騙)
    # credit_score: 信用積分 (預設 100 分)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "rent_app.db")

def get_connection():
    """取得 SQLite 資料庫連線"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 支援字典方式存取資料列
    return conn

def init_db():
    """初始化資料庫表格"""
    # 確保資料庫目錄存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # 建立 users 表格 (包含積分)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            is_verified BOOLEAN DEFAULT 0,
            credit_score INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. 建立 properties 表格 (房源資訊)
    # has_subsidy: 是否有租補
    # tags: 關鍵字標籤，可以儲存逗號分隔的字串 (例如: "落地窗,養寵物,採光好")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            landlord_id INTEGER NOT NULL,
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
    # is_anonymous: 是否匿名留言
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
    # reviewer_id: 給予評分的人
    # target_user_id: 被評分的人
    # score_change: 分數變化量 (例如 +5 或 -10)
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
    # 僅限逢甲信箱認證者可發布
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roommates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            expected_rent INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"資料庫初始化完成！已建立或確認表格存在。資料庫位置：{DB_PATH}")

if __name__ == "__main__":
    # 若直接執行此檔案，則進行資料庫初始化
    init_db()
            role TEXT NOT NULL,  -- 'landlord' or 'tenant'
            total_credit INTEGER DEFAULT 50
        )
    ''')
    
    # 建立 credit_logs 表格
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
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rent_app.db")

def get_connection():
    """取得資料庫連線"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化資料庫與建立表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 建立房源表 (測試用簡化版)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        price INTEGER NOT NULL,
        address TEXT NOT NULL,
        room_type TEXT NOT NULL
    )
    ''')
    
    # 建立標籤關聯表 (與黃柏翰/陳柔溱對齊的格式)
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

if __name__ == "__main__":
    init_db()
    print("資料庫初始化完成！")
def insert_dummy_data():
    """插入測試資料"""
    conn = get_connection()
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
    cursor.executemany('''
        INSERT INTO properties (title, price, address, room_type)
        VALUES (?, ?, ?, ?)
    ''', properties)
    
    # 插入對應標籤 (與 4 大痛點分類對齊)
    # 1: 逢甲大學旁優質套房 -> 離校區5分內, 台水台電, 有外窗, 獨立洗衣機, 免仲介費
    # 2: 全新採光大陽台套房 -> 獨立陽台, 採光好, 乾濕分離, 近捷運, 可申請租補, 電梯大樓
    # 3: 溫馨可養寵物小套房 -> 養寵物, 垃圾代收, 非頂加, 免仲介費, 子母車
    # 4: 近商圈生活機能佳套房 -> 電梯大樓, 垃圾代收, 有小客車/機車位, 離校區5分內, 有外窗
    # 5: 高級乾濕分離家庭房 -> 乾濕分離, 台水台電, 獨立陽台, 落地窗, 電梯大樓, 有小客車/機車位, 垃圾代收
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
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    insert_dummy_data()
    print("資料庫與測試資料已建立完成！")
