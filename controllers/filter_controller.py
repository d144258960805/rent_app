from database.db import get_db_connection

class FilterController:
    @staticmethod
    def get_room_types():
        """回傳系統中所有的房型選項"""
        return ["全部", "獨立套房", "分租套房", "雅房", "整層住家"]

    @staticmethod
    def filter_properties(max_rent=None, room_type="全部", has_subsidy=False):
        """
        依據租金上限、房型、是否可租補進行篩選。
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        # 1. 租金上限篩選
        if max_rent is not None and max_rent > 0:
            query += " AND rent <= ?"
            params.append(max_rent)
            
        # 2. 房型篩選
        if room_type and room_type != "全部":
            query += " AND room_type = ?"
            params.append(room_type)
            
        # 3. 租賃補貼篩選
        if has_subsidy:
            query += " AND has_subsidy = 1"
            
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        # 將 Row 轉成 dict 回傳
        return [dict(row) for row in rows]
