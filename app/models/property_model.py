from app.db import get_db

def get_properties_with_filter(filters):
    """
    根據篩選條件取得房源清單 (F-01 分類篩選)
    """
    db = get_db()
    
    query = "SELECT * FROM properties WHERE 1=1"
    params = []
    
    # 預算與大小
    if filters.get('min_price') and str(filters['min_price']).isdigit():
        query += " AND price >= ?"
        params.append(int(filters['min_price']))
    if filters.get('max_price') and str(filters['max_price']).isdigit():
        query += " AND price <= ?"
        params.append(int(filters['max_price']))
        
    if filters.get('min_size') and str(filters['min_size']).replace('.', '', 1).isdigit():
        query += " AND size >= ?"
        params.append(float(filters['min_size']))
    if filters.get('max_size') and str(filters['max_size']).replace('.', '', 1).isdigit():
        query += " AND size <= ?"
        params.append(float(filters['max_size']))
        
    # 房型與建物
    if filters.get('room_type') and filters['room_type'] != 'all':
        query += " AND room_type = ?"
        params.append(filters['room_type'])
    if filters.get('building_type') and filters['building_type'] != 'all':
        query += " AND building_type = ?"
        params.append(filters['building_type'])
        
    # 布林值開關
    if filters.get('has_subsidy') == '1':
        query += " AND has_subsidy = 1"
    elif filters.get('has_subsidy') == '0':
        query += " AND has_subsidy = 0"
        
    if filters.get('inc_water') == '1': query += " AND inc_water = 1"
    if filters.get('inc_internet') == '1': query += " AND inc_internet = 1"
    if filters.get('inc_management') == '1': query += " AND inc_management = 1"
    if filters.get('inc_cleaning') == '1': query += " AND inc_cleaning = 1"
    
    if filters.get('exclude_rooftop') == '1':
        query += " AND is_rooftop = 0"
    if filters.get('is_certified') == '1':
        query += " AND is_certified = 1"
        
    # 距離與區域
    if filters.get('distance_to_fcu') and str(filters['distance_to_fcu']).isdigit():
        query += " AND distance_to_fcu <= ?"
        params.append(int(filters['distance_to_fcu']))
    if filters.get('fcu_zone') and filters['fcu_zone'] != 'all':
        query += " AND fcu_zone = ?"
        params.append(filters['fcu_zone'])
        
    # 房東類型
    if filters.get('landlord_type') and filters['landlord_type'] != 'all':
        query += " AND landlord_type = ?"
        params.append(filters['landlord_type'])
        
    # 設備與服務 (模糊比對字串)
    equipments = filters.get('equipments', [])
    for eq in equipments:
        if eq: # 確保非空
            query += " AND equipments LIKE ?"
            params.append(f"%{eq}%")
            
    query += " ORDER BY created_at DESC"
    
    properties = db.execute(query, params).fetchall()
    return properties
