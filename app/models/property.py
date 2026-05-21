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
    def get_filtered(query=None, rent_range=None, room_type=None, size_range=None, subsidy_available=None, tag_name=None):
        db = get_db()
        cursor = db.cursor()
        
        sql = """
            SELECT DISTINCT p.*, u.name as landlord_name, u.score as landlord_score
            FROM properties p
            JOIN users u ON p.landlord_id = u.id
            LEFT JOIN property_tags pt ON p.id = pt.property_id
            LEFT JOIN tags t ON pt.tag_id = t.id
            WHERE p.status = 'active'
        """
        params = []

        if query:
            sql += " AND (p.title LIKE ? OR p.description LIKE ? OR p.address LIKE ?)"
            q_param = f"%{query}%"
            params.extend([q_param, q_param, q_param])
            
        if rent_range:
            if rent_range == 'under5000':
                sql += " AND p.rent < 5000"
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
            elif size_range == '5to10':
                sql += " AND p.size >= 5 AND p.size <= 10"
            elif size_range == 'above10':
                sql += " AND p.size > 10"
                
        if subsidy_available == '1' or subsidy_available == True or subsidy_available == 'on':
            sql += " AND p.subsidy_available = 1"
            
        if tag_name:
            sql += " AND t.name = ?"
            params.append(tag_name)
            
        sql += " ORDER BY p.created_at DESC"
        cursor.execute(sql, params)
        return cursor.fetchall()

class Tag:
    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM tags")
        return cursor.fetchall()

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
