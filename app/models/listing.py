"""
app/models/listing.py

Listing Model — 提供房源查詢與篩選方法（F-01 分類篩選）
使用 SQLite，資料庫路徑為 instance/database.db
"""

import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'instance', 'database.db'
)


def get_db_connection():
    """建立並回傳 SQLite 連線，以欄位名稱存取查詢結果。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化資料庫：建立 listings 資料表並寫入示範資料（若尚未存在）。"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS listings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT    NOT NULL,
                address     TEXT    NOT NULL,
                rent        INTEGER NOT NULL,          -- 月租（元）
                room_type   TEXT    NOT NULL,          -- 套房/雅房/整層/分租套房
                size_ping   REAL    NOT NULL,          -- 坪數
                has_subsidy INTEGER NOT NULL DEFAULT 0,-- 租補 1=有 0=無
                tags        TEXT    DEFAULT '',        -- 逗號分隔標籤
                image_url   TEXT    DEFAULT '',
                description TEXT    DEFAULT '',
                created_at  TEXT    DEFAULT (datetime('now','localtime'))
            );

            -- 示範資料（第一次初始化時才插入）
            INSERT OR IGNORE INTO listings
                (id, title, address, rent, room_type, size_ping, has_subsidy, tags, image_url, description)
            VALUES
                (1,  '近逢甲商圈精緻套房', '台中市西屯區逢甲路101號',  7500, '套房',     8.5, 1,
                     '近商圈,獨立衛浴,冷氣,網路',
                     'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600',
                     '位於逢甲商圈核心，步行3分鐘即可到達學校，交通便利，生活機能完善。'),
                (2,  '陽光明媚雅房出租',   '台中市西屯區文華路55號',   5000, '雅房',     5.0, 0,
                     '採光好,近校門,共用衛浴',
                     'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600',
                     '一樓雅房，採光良好，房東親切友善，適合單身學生入住。'),
                (3,  '逢甲整層住家四房',   '台中市西屯區漢翔路30號',  22000, '整層住家', 32.0, 0,
                     '四房,停車位,電梯,管理員',
                     'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600',
                     '整層四房，適合多人分租，電梯大樓，有專人管理，安全有保障。'),
                (4,  '超值分租套房（含租補）', '台中市西屯區福星路20號', 6000, '分租套房', 6.5, 1,
                     '租補,網路,冷氣,洗衣機',
                     'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600',
                     '本房源符合住宅租金補貼資格，房客可申請政府租補，實際月租更划算！'),
                (5,  '精緻小套房近逢甲',    '台中市西屯區上石路88號',   8800, '套房',    10.0, 1,
                     '落地窗,採光好,乾濕分離,近捷運',
                     'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600',
                     '全新裝潢，落地窗採光極佳，乾濕分離衛浴，生活品質一流。'),
                (6,  '溫馨雅房月租5500',    '台中市西屯區永貞路40號',   5500, '雅房',     6.0, 0,
                     '近公車站,安靜,共用廚房',
                     'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=600',
                     '安靜社區，距逢甲步行10分鐘，適合需要安靜學習環境的學生。'),
                (7,  '三房分租套房（附停車）', '台中市西屯區河南路二段99號', 9500, '分租套房', 12.0, 0,
                     '停車位,寵物友善,電梯',
                     'https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600',
                     '三房分租，附停車位，寵物友善，房東好溝通，適合需要養寵物的學生。'),
                (8,  '豪華整層住家（近校門）', '台中市西屯區逢甲路50號', 18000, '整層住家', 28.0, 1,
                     '近校門,豪華裝潢,電梯,租補',
                     'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600',
                     '距逢甲校門步行2分鐘，豪華裝潢，符合租補資格，高性價比選擇。');
        """)
        conn.commit()
    finally:
        conn.close()


def filter_listings(rent_min=0, rent_max=50000, room_types=None,
                    size_min=0.0, size_max=999.0, has_subsidy=None):
    """
    依篩選條件查詢房源列表。

    Args:
        rent_min (int):    最低月租金（元），預設 0
        rent_max (int):    最高月租金（元），預設 50000
        room_types (list): 房型清單，如 ['套房', '雅房']；None 表示全部
        size_min (float):  最小坪數，預設 0
        size_max (float):  最大坪數，預設 999
        has_subsidy (int): 是否有租補：1=有 0=無 None=不限

    Returns:
        list[sqlite3.Row]: 符合條件的房源列表
    """
    conn = get_db_connection()
    try:
        query = "SELECT * FROM listings WHERE rent BETWEEN ? AND ? AND size_ping BETWEEN ? AND ?"
        params = [rent_min, rent_max, size_min, size_max]

        if room_types:
            placeholders = ','.join('?' * len(room_types))
            query += f" AND room_type IN ({placeholders})"
            params.extend(room_types)

        if has_subsidy is not None:
            query += " AND has_subsidy = ?"
            params.append(has_subsidy)

        query += " ORDER BY created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return rows
    except Exception as e:
        print(f"[Listing.filter_listings] 查詢錯誤: {e}")
        return []
    finally:
        conn.close()


def get_by_id(listing_id):
    """
    取得單筆房源。

    Args:
        listing_id (int): 房源 ID

    Returns:
        sqlite3.Row | None
    """
    conn = get_db_connection()
    try:
        row = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
        return row
    except Exception as e:
        print(f"[Listing.get_by_id] 查詢錯誤: {e}")
        return None
    finally:
        conn.close()
