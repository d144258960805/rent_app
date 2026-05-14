from app.db import get_db

def get_properties_with_filter(min_price=None, max_price=None, room_type=None, has_subsidy=None):
    """
    根據篩選條件取得房源清單 (F-01 分類篩選)
    """
    db = get_db()
    
    query = "SELECT * FROM properties WHERE 1=1"
    params = []
    
    if min_price and str(min_price).isdigit():
        query += " AND price >= ?"
        params.append(int(min_price))
        
    if max_price and str(max_price).isdigit():
        query += " AND price <= ?"
        params.append(int(max_price))
        
    if room_type and room_type != 'all':
        query += " AND room_type = ?"
        params.append(room_type)
        
    if has_subsidy is not None and has_subsidy != 'all':
        # 在表單中可能會傳送 '1' 表示有補助，'0' 表示無，'all' 表示不限
        if has_subsidy in ('1', '0'):
            query += " AND has_subsidy = ?"
            params.append(int(has_subsidy))
            
    query += " ORDER BY created_at DESC"
    
    properties = db.execute(query, params).fetchall()
    return properties
