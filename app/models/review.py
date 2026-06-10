# app/models/review.py
from app.models import get_db

class Review:
    @staticmethod
    def create(property_id, author_id, content, rating, image_path=None):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO reviews (property_id, student_id, comment, rating, image_url) 
               VALUES (?, ?, ?, ?, ?)""",
            (property_id, author_id, content, rating, image_path)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_property(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT r.*, u.name as author_name, u.role as author_role 
            FROM reviews r 
            JOIN users u ON r.student_id = u.id 
            WHERE r.property_id = ? 
            ORDER BY r.created_at DESC
        """, (property_id,))
        return cursor.fetchall()

