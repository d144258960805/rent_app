from app.models.db import get_db_connection
import sqlite3

class UserModel:
    @staticmethod
    def create(data):
        """
        新增一筆使用者記錄。
        :param data: dict，包含 role, email, password_hash, name, phone, points, is_verified, created_at
        :return: 新增的記錄 ID
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = '''
                INSERT INTO users (role, email, password_hash, name, phone, points, is_verified, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (
                data.get('role'),
                data.get('email'),
                data.get('password_hash'),
                data.get('name'),
                data.get('phone'),
                data.get('points', 100),
                data.get('is_verified', False),
                data.get('created_at')
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except sqlite3.Error as e:
            print(f"UserModel.create 錯誤: {e}")
            raise

    @staticmethod
    def get_all():
        """
        取得所有使用者記錄。
        :return: list of dicts
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"UserModel.get_all 錯誤: {e}")
            raise

    @staticmethod
    def get_by_id(user_id):
        """
        取得單筆使用者記錄。
        :param user_id: 使用者 ID
        :return: dict 或 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"UserModel.get_by_id 錯誤: {e}")
            raise

    @staticmethod
    def update(user_id, data):
        """
        更新使用者記錄。
        :param user_id: 使用者 ID
        :param data: dict，包含欲更新的欄位與值
        :return: bool，是否更新成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values())
            values.append(user_id)
            
            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"UserModel.update 錯誤: {e}")
            raise

    @staticmethod
    def delete(user_id):
        """
        刪除使用者記錄。
        :param user_id: 使用者 ID
        :return: bool，是否刪除成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"UserModel.delete 錯誤: {e}")
            raise
