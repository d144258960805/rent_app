from app.models import get_db

class User:
    @staticmethod
    def create(email, password_hash, name, role, phone=None, school_email=None):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash, name, role, phone, school_email) VALUES (?, ?, ?, ?, ?, ?)",
            (email, password_hash, name, role, phone, school_email)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
    
    @staticmethod
    def get_by_email(email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        return cursor.fetchone()

    @staticmethod
    def update_score(user_id, new_score):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET score = ? WHERE id = ?", (new_score, user_id))
        db.commit()

    @staticmethod
    def update_school_email(user_id, school_email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET school_email = ? WHERE id = ?", (school_email, user_id))
        db.commit()

    @staticmethod
    def update_profile(user_id, name, phone):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET name = ?, phone = ? WHERE id = ?", (name, phone, user_id))
        db.commit()


class Verification:
    @staticmethod
    def create(user_id, id_card_path, title_deed_path, owner_name=None, property_address=None, status='pending', ai_report=None):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO verifications 
               (user_id, id_card_path, title_deed_path, owner_name, property_address, status, ai_report) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, id_card_path, title_deed_path, owner_name, property_address, status, ai_report)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(verification_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM verifications WHERE id = ?", (verification_id,))
        return cursor.fetchone()
        
    @staticmethod
    def get_pending():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            SELECT v.*, u.email, u.name 
            FROM verifications v 
            JOIN users u ON v.user_id = u.id 
            WHERE v.status = 'pending'
        ''')
        return cursor.fetchall()

    @staticmethod
    def update_status(verification_id, status, reviewer_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE verifications SET status = ?, reviewed_at = CURRENT_TIMESTAMP, reviewer_id = ? WHERE id = ?",
            (status, reviewer_id, verification_id)
        )
        db.commit()
