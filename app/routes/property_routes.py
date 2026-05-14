from flask import Blueprint, render_template, request
from app.models.property_model import get_properties_with_filter

bp = Blueprint('property', __name__, url_prefix='/properties')

@bp.route('/')
def list_properties():
    """
    房源清單與分類篩選 (F-01)
    """
    # 取得 GET 參數
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    room_type = request.args.get('room_type', 'all')
    has_subsidy = request.args.get('has_subsidy', 'all')
    
    # 呼叫 Model 取得篩選後的房源
    properties = get_properties_with_filter(
        min_price=min_price,
        max_price=max_price,
        room_type=room_type,
        has_subsidy=has_subsidy
    )
    
    return render_template('property/list.html', 
                           properties=properties,
                           min_price=min_price,
                           max_price=max_price,
                           room_type=room_type,
                           has_subsidy=has_subsidy)
