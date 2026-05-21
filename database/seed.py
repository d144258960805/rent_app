import sqlite3
import hashlib
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rent_app.db")

def hash_password(password: str) -> str:
    """與 AuthController 一致的 SHA-256 密碼雜湊"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def seed_db():
    if not os.path.exists(DB_PATH):
        print("警告：資料庫檔案不存在，請先執行 database/db.py 初始化表格。")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 清除舊資料以確保每次執行都是乾淨的測試環境
    print("正在清空舊的測試資料...")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM properties")
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM credits")
    cursor.execute("DELETE FROM roommates")
    cursor.execute("DELETE FROM sqlite_sequence") # 重設自動遞增 ID
    conn.commit()

    # 2. 注入使用者資料 (users)
    # id=1: 管理員
    # id=2: 學生 1 (正常積分 100)
    # id=3: 學生 2 (積分 75，低於 80 門檻以測試 F-07)
    # id=4: 房東 1 (已認證，可刊登房源)
    # id=5: 房東 2 (未認證，測試 F-04 驗證功能)
    users_data = [
        ("系統管理員", "admin@fcu.edu.tw", hash_password("admin123"), "admin", 1, 100),
        ("逢甲學生甲", "student1@o365.fcu.edu.tw", hash_password("student123"), "student", 1, 100),
        ("信用受限學生", "student2@o365.fcu.edu.tw", hash_password("student123"), "student", 1, 75),
        ("優良房東張阿姨", "landlord1@fcu.edu.tw", hash_password("landlord123"), "landlord", 1, 100),
        ("待審核房東陳先生", "landlord2@fcu.edu.tw", hash_password("landlord123"), "landlord", 0, 100)
    ]

    print("正在注入使用者資料...")
    cursor.executemany('''
        INSERT INTO users (username, email, password_hash, role, is_verified, credit_score)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', users_data)
    conn.commit()

    # 3. 注入房源資料 (properties)
    # landlord_id = 4 (房東 1: 張阿姨)
    properties_data = [
        (4, "逢甲捷境優質陽台套房", "近逢甲大學側門，走路3分鐘。光線充足、獨立陽台、專人垃圾處理、附獨立洗衣機。", 7500, "獨立套房", 7.5, 1, "落地窗,採光好,乾濕分離,近商圈", "台中市西屯區文華路100號", 24.1786, 120.6465),
        (4, "西安街精緻採光套房 (可貓)", "新裝潢！採光極佳，家具齊全，可帶貓咪。垃圾集中處理，社區 24 點安全門禁管理。", 9000, "分租套房", 8.0, 1, "養寵物,採光好,電梯大樓,免仲介費", "台中市西屯區西安街200號", 24.1812, 120.6450),
        (4, "福星路小資雅房 (超便宜)", "福星商圈鬧中取靜，水電依帳單分攤。非常適合預算有限的逢甲學弟妹，CP值超高！", 5000, "雅房", 5.5, 0, "近商圈,近校區,採光好", "台中市西屯區福星路350號", 24.1755, 120.6442),
        (4, "逢甲頂級樓中樓整層住宅", "適合好朋友一起合租！全新家具、雙衛浴、大客廳與廚房可開伙，前後大陽台通風極佳。", 24000, "整層住家", 22.0, 1, "落地窗,陽台,可開伙,電梯大樓", "台中市西屯區烈美街80號", 24.1805, 120.6420),
        (4, "文華商圈採光獨立單間", "精巧溫馨獨立套房，獨立電表 (一度5元)，免公設比，儲熱式電熱水器超安全。", 6500, "獨立套房", 6.0, 0, "近商圈,近校區,乾濕分離", "台中市西屯區文華路250號", 24.1795, 120.6480)
    ]

    print("正在注入房源資料...")
    cursor.executemany('''
        INSERT INTO properties (landlord_id, title, description, rent, room_type, size, has_subsidy, tags, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', properties_data)
    conn.commit()

    # 4. 注入歷史評論資料 (reviews)
    # user_id = 2 (學生甲) 評論房源 1
    reviews_data = [
        (1, 2, 5, "張阿姨人非常好，修東西很快！套房通風採光都跟照片一模一樣，住了兩年非常滿意！", None, 0),
        (1, 3, 4, "這間雖然便宜，但是隔音稍微差了一點點，不過阿姨人很熱情，總體來說CP值很高！", None, 1),
        (2, 2, 5, "採光真的很棒，社區管理員也很親切，推！而且可以直接養我的橘貓，超幸福的！", None, 0)
    ]

    print("正在注入房源評論...")
    cursor.executemany('''
        INSERT INTO reviews (property_id, user_id, rating, comment, image_url, is_anonymous)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', reviews_data)
    conn.commit()

    # 5. 注入揪室友貼文資料 (roommates)
    # user_id = 2 (學生甲)
    roommates_data = [
        (2, "徵求烈美街整層住家室友 2 名", "目前還缺兩位室友，希望是不抽菸、生活作息正常、注重衛生的逢甲同學。可以私信約時間一起看房！", 6000),
        (2, "西安街優質分租套房徵合租室友", "誠徵愛貓的逢甲室友，男女不限。希望能一起維持客廳的整潔，歡迎聯絡！", 4500)
    ]

    print("正在注入揪室友貼文...")
    cursor.executemany('''
        INSERT INTO roommates (user_id, title, description, expected_rent)
        VALUES (?, ?, ?, ?)
    ''', roommates_data)
    conn.commit()

    # 6. 注入信用異動歷史紀錄 (credits)
    # target_user_id = 3 (學生 2: 信用受限學生) 因違約被扣分
    credits_data = [
        (3, 1, -25, "惡意棄單看房預約，且被多名房東檢舉未準時履約。")
    ]
    
    print("正在注入信用評分異動紀錄...")
    cursor.executemany('''
        INSERT INTO credits (target_user_id, reviewer_id, score_change, reason)
        VALUES (?, ?, ?, ?)
    ''', credits_data)
    conn.commit()

    conn.close()
    print("All test data has been seeded successfully!")

if __name__ == "__main__":
    seed_db()
