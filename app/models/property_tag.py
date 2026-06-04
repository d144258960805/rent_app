from app.models.db import get_db_connection
import sqlite3

class PropertyTagModel:
    @staticmethod
    def create(data):
        """
        新增一筆房源標籤記錄。
        :param data: dict，包含 property_id, tag_name
        :return: 新增的記錄 ID
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO property_tags (property_id, tag_name) VALUES (?, ?)"
            cursor.execute(query, (
                data.get('property_id'),
                data.get('tag_name')
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except sqlite3.Error as e:
            print(f"PropertyTagModel.create 錯誤: {e}")
            raise

    @staticmethod
    def get_all():
        """
        取得所有房源標籤記錄。
        :return: list of dicts
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM property_tags")
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"PropertyTagModel.get_all 錯誤: {e}")
            raise

    @staticmethod
    def get_by_id(tag_id):
        """
        取得單筆房源標籤記錄。
        :param tag_id: 標籤 ID
        :return: dict 或 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM property_tags WHERE id = ?", (tag_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"PropertyTagModel.get_by_id 錯誤: {e}")
            raise

    @staticmethod
    def update(tag_id, data):
        """
        更新房源標籤記錄。
        :param tag_id: 標籤 ID
        :param data: dict，包含欲更新的欄位與值
        :return: bool，是否更新成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values())
            values.append(tag_id)
            
            query = f"UPDATE property_tags SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"PropertyTagModel.update 錯誤: {e}")
            raise

    @staticmethod
    def delete(tag_id):
        """
        刪除房源標籤記錄。
        :param tag_id: 標籤 ID
        :return: bool，是否刪除成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM property_tags WHERE id = ?", (tag_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"PropertyTagModel.delete 錯誤: {e}")
            raise
