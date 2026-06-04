import sqlite3
from database.db import get_connection

class PropertyModel:
    @staticmethod
    def search(keyword="", tags=None):
        """
        根據關鍵字與標籤列表搜尋房源。
        關鍵字會模糊比對標題、地址與房型。
        標籤支援多標籤疊加搜尋（必須同時擁有所有指定的標籤）。
        """
        tags = tags or []
        conn = get_connection()
        cursor = conn.cursor()
        
        params = []
        keyword_cond = ""
        
        if keyword:
            keyword_cond = " AND (p.title LIKE ? OR p.address LIKE ? OR p.room_type LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
            
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
        
    @staticmethod
    def get_all_popular_tags():
        """取得所有出現過的熱門標籤，供 UI 顯示"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT tag_name, COUNT(*) as count 
            FROM property_tags 
            GROUP BY tag_name 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        tags = [row['tag_name'] for row in cursor.fetchall()]
        conn.close()
        return tags
