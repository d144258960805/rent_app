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

    @staticmethod
    def search(keyword="", tags=None):
        """
        根據關鍵字與標籤列表搜尋房源。
        關鍵字會模糊比對標題、地址與房型。
        標籤支援多標籤疊加搜尋（必須同時擁有所有指定的標籤）。
        """
        tags = tags or []
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            params = []
            keyword_cond = ""
            
            if keyword:
                keyword_cond = " AND (p.title LIKE ? OR p.address LIKE ? OR p.room_type LIKE ? OR p.description LIKE ?)"
                params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
                
            if not tags:
                query = f"SELECT p.* FROM properties p WHERE 1=1 {keyword_cond}"
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
            else:
                placeholders = ', '.join(['?'] * len(tags))
                query = f'''
                    SELECT p.*
                    FROM properties p
                    JOIN property_tags pt ON p.id = pt.property_id
                    WHERE 1=1 {keyword_cond}
                    AND pt.tag_name IN ({placeholders})
                    GROUP BY p.id
                    HAVING COUNT(DISTINCT pt.tag_name) = ?
                '''
                params.extend(tags)
                params.append(len(tags))
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                
            # 幫結果附加所有的標籤
            for prop in results:
                cursor.execute("SELECT tag_name FROM property_tags WHERE property_id = ?", (prop['id'],))
                prop['tags'] = [row['tag_name'] for row in cursor.fetchall()]
                
            conn.close()
            return results
        except sqlite3.Error as e:
            print(f"PropertyModel.search 錯誤: {e}")
            raise
            
    @staticmethod
    def get_all_popular_tags():
        """取得所有出現過的熱門標籤，供 UI 顯示"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tag_name, COUNT(*) as count 
                FROM property_tags 
                GROUP BY tag_name 
                ORDER BY count DESC 
                LIMIT 15
            ''')
            tags = [row['tag_name'] for row in cursor.fetchall()]
            conn.close()
            return tags
        except sqlite3.Error as e:
            print(f"PropertyModel.get_all_popular_tags 錯誤: {e}")
            raise
