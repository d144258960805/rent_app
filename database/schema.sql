DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    points INTEGER DEFAULT 100,
    is_verified BOOLEAN DEFAULT 0,
    created_at DATETIME
);

DROP TABLE IF EXISTS properties;
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    landlord_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    address TEXT,
    price INTEGER NOT NULL,
    room_type TEXT,
    size REAL,
    has_subsidy BOOLEAN DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY(landlord_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS property_tags;
CREATE TABLE property_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    FOREIGN KEY(property_id) REFERENCES properties(id)
);

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT,
    created_at DATETIME,
    FOREIGN KEY(property_id) REFERENCES properties(id),
    FOREIGN KEY(student_id) REFERENCES users(id)
);

DROP TABLE IF EXISTS roommate_posts;
CREATE TABLE roommate_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    required_gender TEXT DEFAULT '不限',
    created_at DATETIME,
    FOREIGN KEY(student_id) REFERENCES users(id)
);
