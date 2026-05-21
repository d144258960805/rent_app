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
    FOREIGN KEY (landlord_id) REFERENCES users(id)
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

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    content TEXT,
    image_path TEXT,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id),
    FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS roommate_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
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

-- 預先插入精選特色標籤
INSERT OR IGNORE INTO tags (name) VALUES ('落地窗');
INSERT OR IGNORE INTO tags (name) VALUES ('採光好');
INSERT OR IGNORE INTO tags (name) VALUES ('乾濕分離');
INSERT OR IGNORE INTO tags (name) VALUES ('可養寵物');
INSERT OR IGNORE INTO tags (name) VALUES ('有電梯');
INSERT OR IGNORE INTO tags (name) VALUES ('獨立陽台');
INSERT OR IGNORE INTO tags (name) VALUES ('有管理室');
INSERT OR IGNORE INTO tags (name) VALUES ('近逢甲大學');
