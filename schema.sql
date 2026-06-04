DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS rooms;

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    address TEXT NOT NULL,
    type TEXT NOT NULL,          -- '獨立套房', '雅房', '整層住家'
    price INTEGER NOT NULL,
    size REAL NOT NULL,
    has_subsidy INTEGER NOT NULL, -- 0 (否), 1 (是)
    image_url TEXT,
    tags TEXT,                   -- 用逗號分隔的標籤，例如 '採光極佳,近逢甲大學,免仲介費'
    description TEXT,
    owner_name TEXT,
    owner_phone TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

-- Room 1
INSERT INTO rooms (id, title, address, type, price, size, has_subsidy, image_url, tags, description, owner_name, owner_phone)
VALUES (
    1, 
    '逢甲大學旁 - 採光極佳大套房', 
    '台中市西屯區逢甲路 123 號', 
    '獨立套房', 
    8500, 
    8.0, 
    1, 
    '/static/images/room_demo.png', 
    '採光極佳,近逢甲大學,免仲介費,可申請租補', 
    '這間大套房採光超好，通風佳，樓下就是逢甲大學旁。家具家電全配，有獨立洗衣機與曬衣空間，非常適合學生居住。', 
    '王房東', 
    '0912-345-678'
);

-- Room 2
INSERT INTO rooms (id, title, address, type, price, size, has_subsidy, image_url, tags, description, owner_name, owner_phone)
VALUES (
    2, 
    '逢甲夜市商圈 - 質感北歐風電梯套房', 
    '台中市西屯區文華路 45 號', 
    '獨立套房', 
    7200, 
    6.0, 
    0, 
    '/static/images/room_nordic.png', 
    '近商圈,北歐風,電梯大樓,免仲介費', 
    '位於逢甲夜市旁邊的電梯大樓，高樓層景觀佳，北歐簡約裝潢，安靜且生活機能極為便利。內附獨立衛浴、冷氣與高速網路。', 
    '林房東', 
    '0923-456-789'
);

-- Room 3
INSERT INTO rooms (id, title, address, type, price, size, has_subsidy, image_url, tags, description, owner_name, owner_phone)
VALUES (
    3, 
    '福星路溫馨兩房一廳 - 適合同學合租', 
    '台中市西屯區福星路 320 號', 
    '整層住家', 
    18000, 
    20.0, 
    1, 
    '/static/images/room_living.png', 
    '空間寬敞,採光良好,近校區,可申請租補', 
    '兩房一廳一衛一陽台的溫馨住家，採光通風好，非常適合逢甲同學一起合租分擔房租。社區管理完善，有垃圾集中處理，不用追垃圾車！', 
    '陳房東', 
    '0934-567-890'
);

-- Room 4
INSERT INTO rooms (id, title, address, type, price, size, has_subsidy, image_url, tags, description, owner_name, owner_phone)
VALUES (
    4, 
    '逢甲西門旁 - 經濟超值單人雅房', 
    '台中市西屯區西安街 88 號', 
    '雅房', 
    4500, 
    5.0, 
    0, 
    '/static/images/room_budget.png', 
    '超值特價,限學生,環境單純,近校門', 
    '這間雅房價格非常親民實惠，距離逢甲大學西側校門走路只需 3 分鐘。共用兩套衛浴，室友都是逢甲學生，出入單純安全。', 
    '李房東', 
    '0945-678-901'
);

-- Default review for Room 1
INSERT INTO reviews (room_id, content, image_url, created_at)
VALUES (1, '房間跟照片一模一樣，採光真的很讚，而且離逢甲大學超近！', '/static/images/room_demo.png', '2026-05-21 09:34:51');

-- Default review for Room 2
INSERT INTO reviews (room_id, content, image_url, created_at)
VALUES (2, '樓下就是夜市，但氣密窗隔音滿好的，聽不太到噪音，大推！', NULL, '2026-05-21 11:20:00');
