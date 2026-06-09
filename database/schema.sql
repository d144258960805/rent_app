-- database/schema.sql

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'landlord', 'admin')),
    phone TEXT,
    school_email TEXT,
    score INTEGER DEFAULT 100,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    id_card_path TEXT NOT NULL,
    title_deed_path TEXT NOT NULL,
    owner_name TEXT,
    property_address TEXT,
    ai_report TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed_at DATETIME,
    reviewer_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landlord_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    rent INTEGER NOT NULL,
    room_type TEXT,
    size INTEGER,
    subsidy_available BOOLEAN DEFAULT 0,
    address TEXT,
    image_path TEXT, -- 新增：房源封面圖
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (landlord_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 評論表
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT NOT NULL,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 徵室友貼文表
CREATE TABLE IF NOT EXISTS roommate_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    room_type TEXT,
    gender_preference TEXT,
    lifestyle_rules TEXT,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roommate_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES roommate_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS property_tags (
    property_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (property_id, tag_id),
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 預先插入精選特色標籤（五大分類）

-- 1. 租金與補助
INSERT OR IGNORE INTO tags (name) VALUES ('可申請租補');
INSERT OR IGNORE INTO tags (name) VALUES ('含水費');
INSERT OR IGNORE INTO tags (name) VALUES ('含網路費');
INSERT OR IGNORE INTO tags (name) VALUES ('含管理費');
INSERT OR IGNORE INTO tags (name) VALUES ('含清潔費');

-- 2. 房型與空間
INSERT OR IGNORE INTO tags (name) VALUES ('電梯大樓');
INSERT OR IGNORE INTO tags (name) VALUES ('公寓');
INSERT OR IGNORE INTO tags (name) VALUES ('透天厝');
INSERT OR IGNORE INTO tags (name) VALUES ('非頂樓加蓋');

-- 3. 地點與交通
INSERT OR IGNORE INTO tags (name) VALUES ('近逢甲正門');
INSERT OR IGNORE INTO tags (name) VALUES ('近文華路商圈');
INSERT OR IGNORE INTO tags (name) VALUES ('近僑光');
INSERT OR IGNORE INTO tags (name) VALUES ('近水湳校區');

-- 4. 設備與服務
INSERT OR IGNORE INTO tags (name) VALUES ('冷氣');
INSERT OR IGNORE INTO tags (name) VALUES ('冰箱');
INSERT OR IGNORE INTO tags (name) VALUES ('洗衣機');
INSERT OR IGNORE INTO tags (name) VALUES ('飲水機');
INSERT OR IGNORE INTO tags (name) VALUES ('垃圾代收');
INSERT OR IGNORE INTO tags (name) VALUES ('代收包裹');
INSERT OR IGNORE INTO tags (name) VALUES ('光纖網路');
INSERT OR IGNORE INTO tags (name) VALUES ('Wi-Fi');
INSERT OR IGNORE INTO tags (name) VALUES ('落地窗');
INSERT OR IGNORE INTO tags (name) VALUES ('採光好');
INSERT OR IGNORE INTO tags (name) VALUES ('乾濕分離');
INSERT OR IGNORE INTO tags (name) VALUES ('可養寵物');
INSERT OR IGNORE INTO tags (name) VALUES ('獨立陽台');
INSERT OR IGNORE INTO tags (name) VALUES ('可開伙');

-- 5. 安全與信任
INSERT OR IGNORE INTO tags (name) VALUES ('已認證房東');
INSERT OR IGNORE INTO tags (name) VALUES ('房東直租');
INSERT OR IGNORE INTO tags (name) VALUES ('門禁管理');
INSERT OR IGNORE INTO tags (name) VALUES ('24小時監控');
INSERT OR IGNORE INTO tags (name) VALUES ('消防設備');
INSERT OR IGNORE INTO tags (name) VALUES ('對外窗');
