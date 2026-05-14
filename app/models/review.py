from app.models import get_db

class Review:
    @staticmethod
    def create(property_id, author_id, content, rating, image_path=None):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO reviews (property_id, author_id, content, rating, image_path) 
               VALUES (?, ?, ?, ?, ?)""",
            (property_id, author_id, content, rating, image_path)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_property(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reviews WHERE property_id = ? ORDER BY created_at DESC", (property_id,))
        return cursor.fetchall()
