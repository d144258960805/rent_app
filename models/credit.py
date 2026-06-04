from database.db import get_connection

class CreditLog:
    def __init__(self, id, user_id, action_type, points, description, created_at):
        self.id = id
        self.user_id = user_id
        self.action_type = action_type
        self.points = points
        self.description = description
        self.created_at = created_at

    @classmethod
    def get_logs_by_user(cls, user_id):
        """取得指定用戶的積分歷史紀錄"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM credit_logs WHERE user_id = ? ORDER BY created_at DESC", 
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(**dict(row)) for row in rows]

    @classmethod
    def add_log(cls, user_id, action_type, points, description):
        """新增一筆積分紀錄"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO credit_logs (user_id, action_type, points, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action_type, points, description))
        conn.commit()
        conn.close()
