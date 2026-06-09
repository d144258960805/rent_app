# app/models/property.py
from app.models import get_db

class Property:
    @staticmethod
    def create(landlord_id, title, description, rent, room_type, size, subsidy_available, address, image_path=None):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO properties 
               (landlord_id, title, description, rent, room_type, size, subsidy_available, address, image_path) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (landlord_id, title, description, rent, room_type, size, subsidy_available, address, image_path)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.*, u.name as landlord_name, u.score as landlord_score 
            FROM properties p 
            JOIN users u ON p.landlord_id = u.id 
            WHERE p.status = 'active'
            ORDER BY p.created_at DESC
        """)
        return cursor.fetchall()
        
    @staticmethod
    def get_by_id(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT p.*, u.name as landlord_name, u.score as landlord_score, u.email as landlord_email, u.phone as landlord_phone 
            FROM properties p 
            JOIN users u ON p.landlord_id = u.id 
            WHERE p.id = ?
        """, (property_id,))
        return cursor.fetchone()

    @staticmethod
    def delete(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE properties SET status = 'inactive' WHERE id = ?", (property_id,))
        db.commit()

    @staticmethod
    def get_tags(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT t.* FROM tags t 
            JOIN property_tags pt ON t.id = pt.tag_id 
            WHERE pt.property_id = ?
        """, (property_id,))
        return cursor.fetchall()

    @staticmethod
    def get_filtered(query=None, rent_range=None, room_type=None, size_range=None, subsidy_available=None, tag_name=None, tag_names=None, building_type=None):
        db = get_db()
        cursor = db.cursor()
        
        sql = """
            SELECT DISTINCT p.*, u.name as landlord_name, u.score as landlord_score
            FROM properties p
            JOIN users u ON p.landlord_id = u.id
        """
        params = []

        # 如果有標籤篩選，需要 JOIN tags
        has_tag_filter = tag_name or tag_names
        if has_tag_filter:
            sql += " LEFT JOIN property_tags pt ON p.id = pt.property_id"
            sql += " LEFT JOIN tags t ON pt.tag_id = t.id"

        sql += " WHERE p.status = 'active'"

        if query:
            sql += " AND (p.title LIKE ? OR p.description LIKE ? OR p.address LIKE ?)"
            q_param = f"%{query}%"
            params.extend([q_param, q_param, q_param])
            
        if rent_range:
            if rent_range == 'under5000':
                sql += " AND p.rent < 5000"
            elif rent_range == '5000to8000':
                sql += " AND p.rent >= 5000 AND p.rent <= 8000"
            elif rent_range == '8000to12000':
                sql += " AND p.rent >= 8000 AND p.rent <= 12000"
            elif rent_range == 'above12000':
                sql += " AND p.rent > 12000"
            # 向下相容舊值
            elif rent_range == '5000to10000':
                sql += " AND p.rent >= 5000 AND p.rent <= 10000"
            elif rent_range == '10000to15000':
                sql += " AND p.rent >= 10000 AND p.rent <= 15000"
            elif rent_range == 'above15000':
                sql += " AND p.rent > 15000"
                
        if room_type:
            sql += " AND p.room_type = ?"
            params.append(room_type)
            
        if size_range:
            if size_range == 'under5':
                sql += " AND p.size < 5"
            elif size_range == '5to8':
                sql += " AND p.size >= 5 AND p.size <= 8"
            elif size_range == '8to10':
                sql += " AND p.size >= 8 AND p.size <= 10"
            elif size_range == 'above10':
                sql += " AND p.size > 10"
            # 向下相容
            elif size_range == '5to10':
                sql += " AND p.size >= 5 AND p.size <= 10"
                
        if subsidy_available == '1' or subsidy_available == True or subsidy_available == 'on':
            sql += " AND p.subsidy_available = 1"
            
        # 單一標籤（相容舊版）
        if tag_name and not tag_names:
            sql += " AND t.name = ?"
            params.append(tag_name)

        # 多標籤篩選（所有選中標籤都必須匹配）
        if tag_names:
            tag_list = [t for t in tag_names if t]
            if tag_list:
                sql += f"""
                    AND p.id IN (
                        SELECT pt2.property_id FROM property_tags pt2
                        JOIN tags t2 ON pt2.tag_id = t2.id
                        WHERE t2.name IN ({','.join('?' * len(tag_list))})
                        GROUP BY pt2.property_id
                        HAVING COUNT(DISTINCT t2.name) = ?
                    )
                """
                params.extend(tag_list)
                params.append(len(tag_list))
            
        sql += " ORDER BY p.created_at DESC"
        cursor.execute(sql, params)
        return cursor.fetchall()

class Tag:
    # 五大分類對應的標籤
    GROUPED_TAGS = {
        '租金與補助': ['可申請租補', '含水費', '含網路費', '含管理費', '含清潔費'],
        '房型與空間': ['電梯大樓', '公寓', '透天厝', '非頂樓加蓋'],
        '地點與交通': ['近逢甲正門', '近文華路商圈', '近僑光', '近水湳校區'],
        '設備與服務': ['冷氣', '冰箱', '洗衣機', '飲水機', '垃圾代收', '代收包裹', '光纖網路', 'Wi-Fi', '落地窗', '採光好', '乾濕分離', '可養寵物', '獨立陽台', '可開伙'],
        '安全與信任': ['已認證房東', '房東直租', '門禁管理', '24小時監控', '消防設備', '對外窗'],
    }
    
    CATEGORY_ICONS = {
        '租金與補助': '💰',
        '房型與空間': '🏠',
        '地點與交通': '📍',
        '設備與服務': '🔧',
        '安全與信任': '🛡️',
    }

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tags")
        return cursor.fetchall()

    @staticmethod
    def get_grouped():
        """回傳分組後的標籤結構，供風琴式面板使用"""
        return Tag.GROUPED_TAGS, Tag.CATEGORY_ICONS

    @staticmethod
    def add_to_property(property_id, tag_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT OR IGNORE INTO property_tags (property_id, tag_id) VALUES (?, ?)", (property_id, tag_id))
        db.commit()
        
    @staticmethod
    def clear_property_tags(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM property_tags WHERE property_id = ?", (property_id,))
        db.commit()

