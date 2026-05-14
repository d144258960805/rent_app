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
