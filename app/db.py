import sqlite3
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # 讓查詢結果能透過欄位名稱存取 (類似字典)
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # 讀取 schema.sql 建立資料表
    with current_app.open_resource('../database/schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
        
    # 建立測試資料以利 F-01 分類篩選測試
    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM users")
    if cursor.fetchone()[0] == 0:
        db.executescript("""
            INSERT INTO users (username, email, password_hash, role) VALUES ('Test Landlord', 'landlord@test.com', 'hash', 'landlord');
            
            INSERT INTO properties (landlord_id, title, description, price, room_type, size, has_subsidy, tags, address) 
            VALUES (1, '逢甲大學旁採光套房', '近逢甲夜市，採光佳', 6000, '獨立套房', 6.5, 1, '落地窗,乾濕分離', '台中市西屯區逢甲路1號');
            
            INSERT INTO properties (landlord_id, title, description, price, room_type, size, has_subsidy, tags, address) 
            VALUES (1, '溫馨分租套房可養寵', '適合學生合租，可養貓', 4500, '分租套房', 5.0, 0, '養寵物,有陽台', '台中市西屯區福星路10號');
            
            INSERT INTO properties (landlord_id, title, description, price, room_type, size, has_subsidy, tags, address) 
            VALUES (1, '超平價雅房包水電', '適合預算有限的學生', 3000, '雅房', 4.0, 1, '包水電,垃圾代收', '台中市西屯區西安街5號');
            
            INSERT INTO properties (landlord_id, title, description, price, room_type, size, has_subsidy, tags, address) 
            VALUES (1, '豪華獨立套房', '全新裝潢，電梯大樓', 8500, '獨立套房', 8.0, 0, '電梯大樓,台水台電,獨立洗衣機', '台中市西屯區文華路100號');
        """)
        db.commit()

@click.command('init-db')
def init_db_command():
    """清除現有資料並建立新資料表"""
    init_db()
    click.echo('Initialized the database with test data.')

def init_app(app):
    # 確保 request 結束時關閉資料庫連線
    app.teardown_appcontext(close_db)
    # 加入 flask 指令
    app.cli.add_command(init_db_command)
