from app.models.db import get_db_connection
import sqlite3

class ReviewModel:
    @staticmethod
    def create(data):
        """
        新增一筆評論記錄。
        :param data: dict，包含 property_id, student_id, content, image_url, created_at
        :return: 新增的記錄 ID
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = '''
                INSERT INTO reviews (property_id, student_id, content, image_url, created_at)
                VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (
                data.get('property_id'),
                data.get('student_id'),
                data.get('content'),
                data.get('image_url'),
                data.get('created_at')
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except sqlite3.Error as e:
            print(f"ReviewModel.create 錯誤: {e}")
            raise

    @staticmethod
    def get_all():
        """
        取得所有評論記錄。
        :return: list of dicts
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews")
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"ReviewModel.get_all 錯誤: {e}")
            raise

    @staticmethod
    def get_by_id(review_id):
        """
        取得單筆評論記錄。
        :param review_id: 評論 ID
        :return: dict 或 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"ReviewModel.get_by_id 錯誤: {e}")
            raise

    @staticmethod
    def update(review_id, data):
        """
        更新評論記錄。
        :param review_id: 評論 ID
        :param data: dict，包含欲更新的欄位與值
        :return: bool，是否更新成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values())
            values.append(review_id)
            
            query = f"UPDATE reviews SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"ReviewModel.update 錯誤: {e}")
            raise

    @staticmethod
    def delete(review_id):
        """
        刪除評論記錄。
        :param review_id: 評論 ID
        :return: bool，是否刪除成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"ReviewModel.delete 錯誤: {e}")
            raise
