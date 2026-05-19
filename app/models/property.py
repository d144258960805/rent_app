from app.models.db import get_db_connection
import sqlite3

class PropertyModel:
    @staticmethod
    def create(data):
        """
        新增一筆房源記錄。
        :param data: dict，包含 landlord_id, title, description, address, price, room_type, size, has_subsidy, created_at, updated_at
        :return: 新增的記錄 ID
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = '''
                INSERT INTO properties (landlord_id, title, description, address, price, room_type, size, has_subsidy, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (
                data.get('landlord_id'),
                data.get('title'),
                data.get('description'),
                data.get('address'),
                data.get('price'),
                data.get('room_type'),
                data.get('size'),
                data.get('has_subsidy', False),
                data.get('created_at'),
                data.get('updated_at')
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return new_id
        except sqlite3.Error as e:
            print(f"PropertyModel.create 錯誤: {e}")
            raise

    @staticmethod
    def get_all():
        """
        取得所有房源記錄。
        :return: list of dicts
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM properties")
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"PropertyModel.get_all 錯誤: {e}")
            raise

    @staticmethod
    def get_by_id(property_id):
        """
        取得單筆房源記錄。
        :param property_id: 房源 ID
        :return: dict 或 None
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"PropertyModel.get_by_id 錯誤: {e}")
            raise

    @staticmethod
    def update(property_id, data):
        """
        更新房源記錄。
        :param property_id: 房源 ID
        :param data: dict，包含欲更新的欄位與值
        :return: bool，是否更新成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            values = list(data.values())
            values.append(property_id)
            
            query = f"UPDATE properties SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"PropertyModel.update 錯誤: {e}")
            raise

    @staticmethod
    def delete(property_id):
        """
        刪除房源記錄。
        :param property_id: 房源 ID
        :return: bool，是否刪除成功
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.Error as e:
            print(f"PropertyModel.delete 錯誤: {e}")
            raise
