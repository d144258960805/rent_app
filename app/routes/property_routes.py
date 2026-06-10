from flask import Blueprint, render_template, request
from app.models.property_model import get_properties_with_filter

bp = Blueprint('property_list', __name__, url_prefix='/properties')

@bp.route('/')
def list_properties():
    """
    房源清單與分類篩選 (F-01 進階版)
    """
    # 收集所有的過濾參數打包成字典
    filters = {
        'min_price': request.args.get('min_price', ''),
        'max_price': request.args.get('max_price', ''),
        'min_size': request.args.get('min_size', ''),
        'max_size': request.args.get('max_size', ''),
        'room_type': request.args.get('room_type', 'all'),
        'building_type': request.args.get('building_type', 'all'),
        'has_subsidy': request.args.get('has_subsidy', 'all'),
        
        'inc_water': request.args.get('inc_water'),
        'inc_internet': request.args.get('inc_internet'),
        'inc_management': request.args.get('inc_management'),
        'inc_cleaning': request.args.get('inc_cleaning'),
        
        'exclude_rooftop': request.args.get('exclude_rooftop'),
        'is_certified': request.args.get('is_certified'),
        
        'distance_to_fcu': request.args.get('distance_to_fcu', ''),
        'fcu_zone': request.args.get('fcu_zone', 'all'),
        'landlord_type': request.args.get('landlord_type', 'all'),
        
        # getlist 會取得所有 name="equipments" 的核取方塊值
        'equipments': request.args.getlist('equipments')
    }
    
    # 呼叫 Model 取得篩選後的房源
    properties = get_properties_with_filter(filters)
    
    return render_template('property/list.html', 
                           properties=properties,
                           filters=filters)
