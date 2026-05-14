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
        cursor.execute("SELECT * FROM roommate_posts ORDER BY created_at DESC")
        return cursor.fetchall()
        
    @staticmethod
    def update_status(post_id, status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE roommate_posts SET status = ? WHERE id = ?", (status, post_id))
        db.commit()
