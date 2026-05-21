# app/models/roommate.py
from app.models import get_db

class RoommatePost:
    @staticmethod
    def create(author_id, title, content):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO roommate_posts (author_id, title, content) VALUES (?, ?, ?)",
            (author_id, title, content)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT r.*, u.name as author_name, u.school_email as author_school_email 
            FROM roommate_posts r 
            JOIN users u ON r.author_id = u.id 
            ORDER BY r.created_at DESC
        """)
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
