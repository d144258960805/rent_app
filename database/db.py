import sqlite3
import os

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
        ("近商圈生活機能佳", 7000, "西屯區西安街10號", "獨立套房"),
        ("高級乾濕分離家庭房", 15000, "西屯區河南路二段", "整層住家")
    ]
    cursor.executemany('''
        INSERT INTO properties (title, price, address, room_type)
        VALUES (?, ?, ?, ?)
    ''', properties)
    
    # 插入對應標籤
    tags = [
        (1, "落地窗"), (1, "採光好"), (1, "台水台電"),
        (2, "獨立陽台"), (2, "採光好"), (2, "乾濕分離"),
        (3, "養寵物"), (3, "子母車"),
        (4, "落地窗"), (4, "子母車"),
        (5, "乾濕分離"), (5, "台水台電"), (5, "獨立陽台"), (5, "落地窗")
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
