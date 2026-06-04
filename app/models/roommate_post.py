from app.models.db import get_db_connection
import sqlite3

class RoommatePostModel:
    @staticmethod
    def create(data):
        """
        新增一筆找室友貼文記錄。
        :param data: dict，包含 student_id, title, content, required_gender, created_at
        :return: 新增的記錄 ID
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = '''
                INSERT INTO roommate_posts (student_id, title, content, required_gender, created_at)
                VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (
                data.get('student_id'),
                data.get('title'),
                data.get('content'),
                data.get('required_gender'),
                data.get('created_at')
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except sqlite3.Error as e:
            print(f"RoommatePostModel.create 錯誤: {e}")
            raise

    @staticmethod
    def get_all():
        """
        取得所有找室友貼文記錄。
        :return: list of dicts
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roommate_posts")
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"RoommatePostModel.get_all 錯誤: {e}")
            raise

    @staticmethod
    def get_by_id(post_id):
        """
        取得單筆找室友貼文記錄。
        :param post_id: 貼文 ID
        :return: dict 或 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roommate_posts WHERE id = ?", (post_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"RoommatePostModel.get_by_id 錯誤: {e}")
            raise

    @staticmethod
    def update(post_id, data):
        """
        更新找室友貼文記錄。
        :param post_id: 貼文 ID
        :param data: dict，包含欲更新的欄位與值
        :return: bool，是否更新成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values())
            values.append(post_id)
            
            query = f"UPDATE roommate_posts SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"RoommatePostModel.update 錯誤: {e}")
            raise

    @staticmethod
    def delete(post_id):
        """
        刪除找室友貼文記錄。
        :param post_id: 貼文 ID
        :return: bool，是否刪除成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM roommate_posts WHERE id = ?", (post_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"RoommatePostModel.delete 錯誤: {e}")
            raise
