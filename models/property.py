import sqlite3
from database.db import get_connection

class PropertyModel:
    @staticmethod
    def search_by_tags(tags):
        """
        根據標籤列表搜尋房源。
        支援多標籤疊加搜尋（必須同時擁有所有指定的標籤）。
        如果標籤列表為空，則回傳所有房源。
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        if not tags:
            cursor.execute("SELECT * FROM properties")
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return results
            
        # 若有多個標籤，我們需要找到同時擁有這些標籤的 property_id
        # 方法：用 GROUP BY property_id HAVING COUNT(tag_name) = ?
        placeholders = ', '.join(['?'] * len(tags))
        query = f'''
            SELECT p.*
            FROM properties p
            JOIN property_tags pt ON p.id = pt.property_id
            WHERE pt.tag_name IN ({placeholders})
            GROUP BY p.id
            HAVING COUNT(DISTINCT pt.tag_name) = ?
        '''
        
        # 參數包含標籤列表與標籤數量
        params = list(tags) + [len(tags)]
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
