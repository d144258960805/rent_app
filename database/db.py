import sqlite3
import os

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
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("資料庫初始化完成！")
