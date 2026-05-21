from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.property import PropertyModel
from datetime import datetime

property_bp = Blueprint('property_bp', __name__, url_prefix='/properties')

@property_bp.route('/')
def index():
    keyword = request.args.get('keyword', '').strip()
    tags = request.args.getlist('tags')
    
    # 呼叫 Model 進行標籤交集模糊搜尋
    properties = PropertyModel.search(keyword=keyword, tags=tags)
    
    # 提供給 Web 前端渲染的分類標籤痛點資料
    categories = [
        {
            "title": "空間與採光",
            "desc": "隱私、安全與曬衣便利",
            "tags": ["獨立陽台", "非頂加", "有外窗", "落地窗", "採光好"]
        },
        {
            "title": "衛浴與生活",
            "desc": "不追垃圾車、不共用洗衣機",
            "tags": ["獨立洗衣機", "垃圾代收", "電梯大樓", "乾濕分離", "養寵物", "子母車"]
        },
        {
            "title": "費用與合約",
            "desc": "補貼與台水電大省錢！",
            "tags": ["台水台電", "免仲介費", "可申請租補"]
        },
        {
            "title": "周邊與交通",
            "desc": "攸關通勤與遲到機率",
            "tags": ["近捷運", "離校區5分內", "有小客車/機車位"]
        }
    ]
    
    return render_template(
        'properties/index.html', 
        properties=properties, 
        keyword=keyword, 
        selected_tags=tags,
        categories=categories
    )

@property_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        landlord_id = request.form.get('landlord_id')
        price = request.form.get('price')

        if not title or not landlord_id or not price:
            flash('請填寫所有必填欄位 (標題, 房東ID, 租金)！', 'error')
            return render_template('properties/create.html')

        data = {
            'landlord_id': landlord_id,
            'title': title,
            'description': request.form.get('description', ''),
            'address': request.form.get('address', ''),
            'price': price,
            'room_type': request.form.get('room_type', ''),
            'size': request.form.get('size', 0),
            'has_subsidy': True if request.form.get('has_subsidy') == 'on' else False,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            PropertyModel.create(data)
            flash('新增房源成功！', 'success')
            return redirect(url_for('property_bp.index'))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('properties/create.html')

    return render_template('properties/create.html')

@property_bp.route('/<int:property_id>')
def view(property_id):
    property_data = PropertyModel.get_by_id(property_id)
    if not property_data:
        flash('找不到該房源！', 'error')
        return redirect(url_for('property_bp.index'))
    return render_template('properties/view.html', property=property_data)

@property_bp.route('/<int:property_id>/edit', methods=['GET', 'POST'])
def edit(property_id):
    property_data = PropertyModel.get_by_id(property_id)
    if not property_data:
        flash('找不到該房源！', 'error')
        return redirect(url_for('property_bp.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        price = request.form.get('price')
        
        if not title or not price:
            flash('標題與租金為必填！', 'error')
            return render_template('properties/edit.html', property=property_data)

        data = {
            'title': title,
            'price': price,
            'description': request.form.get('description', ''),
            'address': request.form.get('address', ''),
            'room_type': request.form.get('room_type', ''),
            'size': request.form.get('size', 0),
            'has_subsidy': True if request.form.get('has_subsidy') == 'on' else False,
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            PropertyModel.update(property_id, data)
            flash('房源更新成功！', 'success')
            return redirect(url_for('property_bp.view', property_id=property_id))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('properties/edit.html', property=property_data)

    return render_template('properties/edit.html', property=property_data)

@property_bp.route('/<int:property_id>/delete', methods=['POST'])
def delete(property_id):
    try:
        PropertyModel.delete(property_id)
        flash('房源已成功刪除！', 'success')
    except Exception as e:
        flash(f'刪除時發生錯誤: {str(e)}', 'error')
    return redirect(url_for('property_bp.index'))
