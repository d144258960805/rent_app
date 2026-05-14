from app.models import get_db

class Property:
    @staticmethod
    def create(landlord_id, title, description, rent, room_type, size, subsidy_available, address):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO properties 
               (landlord_id, title, description, rent, room_type, size, subsidy_available, address) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (landlord_id, title, description, rent, room_type, size, subsidy_available, address)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def get_all():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM properties WHERE status = 'active'")
        return cursor.fetchall()
        
    @staticmethod
    def get_by_id(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
        return cursor.fetchone()

    @staticmethod
    def delete(property_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE properties SET status = 'inactive' WHERE id = ?", (property_id,))
        db.commit()

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
