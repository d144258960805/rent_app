-- 使用者表 (包含學生與房東)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'landlord', 'admin')),
    points INTEGER DEFAULT 100,
    is_verified BOOLEAN DEFAULT 0,
    document_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 房源表
CREATE TABLE IF NOT EXISTS properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landlord_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    price INTEGER NOT NULL,
    room_type TEXT NOT NULL,
    size REAL NOT NULL,
    has_subsidy BOOLEAN DEFAULT 0,
    inc_water BOOLEAN DEFAULT 0,
    inc_internet BOOLEAN DEFAULT 0,
    inc_management BOOLEAN DEFAULT 0,
    inc_cleaning BOOLEAN DEFAULT 0,
    building_type TEXT,
    is_rooftop BOOLEAN DEFAULT 0,
    distance_to_fcu INTEGER,
    fcu_zone TEXT,
    equipments TEXT,
    landlord_type TEXT,
    is_certified BOOLEAN DEFAULT 0,
    tags TEXT,
    address TEXT NOT NULL,
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
    student_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);
