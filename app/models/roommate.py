# app/models/roommate.py
from app.models import get_db

class RoommatePost:
    @staticmethod
    def create(author_id, title, content, room_type=None, gender_preference=None, lifestyle_rules=None):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO roommate_posts (author_id, title, content, room_type, gender_preference, lifestyle_rules) VALUES (?, ?, ?, ?, ?, ?)",
            (author_id, title, content, room_type, gender_preference, lifestyle_rules)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all(room_type=None, gender_preference=None):
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT r.*, u.name as author_name, u.school_email as author_school_email 
            FROM roommate_posts r 
            JOIN users u ON r.author_id = u.id 
            WHERE 1=1
        """
        params = []
        if room_type and room_type != '全部':
            query += " AND r.room_type = ?"
            params.append(room_type)
        if gender_preference and gender_preference != '全部':
            query += " AND r.gender_preference = ?"
            params.append(gender_preference)
            
        query += " ORDER BY r.created_at DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
        
    @staticmethod
    def get_by_id(post_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT r.*, u.name as author_name, u.school_email as author_school_email, u.phone as author_phone 
            FROM roommate_posts r 
            JOIN users u ON r.author_id = u.id 
            WHERE r.id = ?
        """, (post_id,))
        return cursor.fetchone()
        
    @staticmethod
    def update_status(post_id, status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE roommate_posts SET status = ? WHERE id = ?", (status, post_id))
        db.commit()

    @staticmethod
    def add_comment(post_id, author_id, content):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO roommate_comments (post_id, author_id, content) VALUES (?, ?, ?)",
            (post_id, author_id, content)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_comments(post_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT rc.*, u.name as author_name, u.school_email as author_school_email, u.role as author_role
            FROM roommate_comments rc 
            JOIN users u ON rc.author_id = u.id 
            WHERE rc.post_id = ? 
            ORDER BY rc.created_at ASC
        """, (post_id,))
        return cursor.fetchall()
