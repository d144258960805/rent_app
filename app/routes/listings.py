"""
app/routes/listings.py

F-01 分類篩選路由
- GET /          → 首頁（重導向至房源列表）
- GET /listings  → 接收篩選條件，查詢並顯示房源
- GET /listing/<id> → 單筆房源詳細頁
"""

from flask import Blueprint, render_template, request, redirect, url_for

listings_bp = Blueprint('listings', __name__)

# 合法房型清單
VALID_ROOM_TYPES = ['套房', '雅房', '整層住家', '分租套房']


@listings_bp.route('/')
def index():
    """首頁：直接重導向至房源列表。"""
    return redirect(url_for('listings.listing_list'))


@listings_bp.route('/listings')
def listing_list():
    """
    F-01 分類篩選主路由。
    接收 GET 參數：rent_min, rent_max, room_type (multi), size_min, size_max, has_subsidy
    """
    from app.models.listing import filter_listings

    # ── 1. 取得並驗證篩選參數 ──────────────────────────────────────────────
    try:
        rent_min = int(request.args.get('rent_min', 0))
        rent_max = int(request.args.get('rent_max', 50000))
    except ValueError:
        rent_min, rent_max = 0, 50000

    # 防呆：確保 min <= max
    if rent_min > rent_max:
        rent_min, rent_max = rent_max, rent_min

    try:
        size_min = float(request.args.get('size_min', 0))
        size_max = float(request.args.get('size_max', 999))
    except ValueError:
        size_min, size_max = 0.0, 999.0

    # 房型：可多選，getlist 回傳 list
    room_types_raw = request.args.getlist('room_type')
    room_types = [rt for rt in room_types_raw if rt in VALID_ROOM_TYPES] or None

    # 租補：'1' → 有、'0' → 無、'' 或未帶 → 不限
    subsidy_raw = request.args.get('has_subsidy', '')
    if subsidy_raw == '1':
        has_subsidy = 1
    elif subsidy_raw == '0':
        has_subsidy = 0
    else:
        has_subsidy = None

    # ── 2. 查詢 Model ──────────────────────────────────────────────────────
    listings = filter_listings(
        rent_min=rent_min,
        rent_max=rent_max,
        room_types=room_types,
        size_min=size_min,
        size_max=size_max,
        has_subsidy=has_subsidy,
    )

    # ── 3. 整理已選篩選條件（傳給模板顯示 tag chips）────────────────────────
    active_filters = []
    if rent_min > 0 or rent_max < 50000:
        active_filters.append(f'租金 ${rent_min:,}–${rent_max:,}')
    if room_types:
        active_filters.append('房型：' + '、'.join(room_types))
    if size_min > 0 or size_max < 999:
        active_filters.append(f'坪數 {size_min}–{size_max} 坪')
    if has_subsidy == 1:
        active_filters.append('✓ 有租補')
    elif has_subsidy == 0:
        active_filters.append('✗ 無租補')

    # 傳回表單目前值（讓 Jinja2 預填）
    filters = {
        'rent_min': rent_min,
        'rent_max': rent_max,
        'room_types': room_types or [],
        'size_min': size_min,
        'size_max': size_max,
        'has_subsidy': subsidy_raw,
    }

    return render_template(
        'listings/index.html',
        listings=listings,
        filters=filters,
        active_filters=active_filters,
        total=len(listings),
        valid_room_types=VALID_ROOM_TYPES,
    )


@listings_bp.route('/listing/<int:listing_id>')
def detail(listing_id):
    """單筆房源詳細頁。"""
    from app.models.listing import get_by_id
    listing = get_by_id(listing_id)
    return render_template('listings/detail.html', listing=listing)
