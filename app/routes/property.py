# app/routes/property.py
import os
from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
from app.models.user import User
from app.models.property import Property, Tag
from app.models.review import Review
from app.models import get_db

bp = Blueprint('property', __name__, url_prefix='/property')

def landlord_verified_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入', 'error')
            return redirect(url_for('auth.login'))
            
        if session.get('user_role') != 'landlord':
            flash('只有房東可以刊登房源', 'error')
            return redirect(url_for('index'))
            
        # Check verification status
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT status FROM verifications WHERE user_id = ? ORDER BY submitted_at DESC LIMIT 1",
            (session['user_id'],)
        )
        verification = cursor.fetchone()
        
        if not verification:
            flash('您必須先上傳證明文件並通過審核，才能刊登房源', 'error')
            return redirect(url_for('auth.upload_docs'))
            
        if verification['status'] == 'pending':
            flash('您的證明文件正在審核中，請耐心等候', 'error')
            return redirect(url_for('index'))
            
        if verification['status'] == 'rejected':
            flash('您的證明文件已被拒絕，請重新上傳', 'error')
            return redirect(url_for('auth.upload_docs'))
            
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/post', methods=('GET', 'POST'))
@landlord_verified_required
def post():
    # Check credit score restriction
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT score FROM users WHERE id = ?", (session['user_id'],))
    user_score = cursor.fetchone()['score']
    
    if user_score < 80:
        flash('❌ 您的信用積分過低（低於 80 分），已暫時限制您的房源刊登權限！', 'error')
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        rent = request.form.get('rent')
        room_type = request.form.get('room_type')
        size = request.form.get('size')
        address = request.form.get('address')
        subsidy_available = 1 if request.form.get('subsidy_available') else 0
        selected_tags = request.form.getlist('tags')
        cover_image = request.files.get('cover_image')

        error = None
        if not title or not rent or not room_type or not size or not address:
            error = '標題、租金、房型、坪數與地址為必填欄位。'

        if error is None:
            image_path = None
            if cover_image and cover_image.filename:
                image_filename = secure_filename(cover_image.filename)
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                local_filename = f"prop_{session['user_id']}_{image_filename}"
                cover_image.save(os.path.join(upload_folder, local_filename))
                image_path = f"uploads/{local_filename}"

            property_id = Property.create(
                landlord_id=session['user_id'],
                title=title,
                description=description,
                rent=int(rent),
                room_type=room_type,
                size=int(size),
                subsidy_available=subsidy_available,
                address=address,
                image_path=image_path
            )

            # Save tags relationship
            for tag_id in selected_tags:
                Tag.add_to_property(property_id, int(tag_id))

            flash('🎉 房源上架成功！已順利發布至首頁清單。', 'success')
            return redirect(url_for('property.detail', property_id=property_id))

        flash(error, 'error')

    tags = Tag.get_all()
    return render_template('property/post.html', tags=tags, score=user_score)

@bp.route('/<int:property_id>')
def detail(property_id):
    prop = Property.get_by_id(property_id)
    if not prop:
        flash('找不到該房源！', 'error')
        return redirect(url_for('index'))
        
    reviews = Review.get_by_property(property_id)
    tags = Property.get_tags(property_id)
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r['rating'] for r in reviews) / len(reviews), 1)

    # Check user score if logged in
    user_score = 100
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT score FROM users WHERE id = ?", (session['user_id'],))
        user_score = cursor.fetchone()['score']

    return render_template(
        'property/detail.html',
        property=prop,
        reviews=reviews,
        tags=tags,
        avg_rating=avg_rating,
        user_score=user_score
    )

@bp.route('/<int:property_id>/review', methods=('POST',))
def upload_review(property_id):
    if 'user_id' not in session:
        flash('請先登入後再填寫真實評論。', 'error')
        return redirect(url_for('auth.login'))
        
    rating = request.form.get('rating')
    content = request.form.get('content')
    review_image = request.files.get('review_image')
    
    if not rating or not content:
        flash('請選擇星等評分並填寫實屋短評。', 'error')
        return redirect(url_for('property.detail', property_id=property_id))
        
    image_path = None
    if review_image and review_image.filename:
        image_filename = secure_filename(review_image.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        local_filename = f"rev_{session['user_id']}_{image_filename}"
        review_image.save(os.path.join(upload_folder, local_filename))
        image_path = f"uploads/{local_filename}"
        
    Review.create(
        property_id=property_id,
        author_id=session['user_id'],
        content=content,
        rating=int(rating),
        image_path=image_path
    )
    
    flash('🎉 真實屋況短評上傳成功！感謝您的真實回饋協助學弟妹防範落差。', 'success')
    return redirect(url_for('property.detail', property_id=property_id))

@bp.route('/<int:property_id>/reserve', methods=('POST',))
def reserve(property_id):
    if 'user_id' not in session:
        flash('請先登入後再進行看房預約。', 'error')
        return redirect(url_for('auth.login'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT score FROM users WHERE id = ?", (session['user_id'],))
    user_score = cursor.fetchone()['score']
    
    if user_score < 80:
        flash('❌ 看房預約失敗：您的信用評分低於 80 分，已被系統暫時鎖定預約功能！', 'error')
        return redirect(url_for('property.detail', property_id=property_id))
        
    # Simulate reservation save
    flash('🎉 看房預約申請成功！系統已將您的聯絡電話發送給房東，房東將於 24 小時內與您聯繫。', 'success')
    return redirect(url_for('property.detail', property_id=property_id))

@bp.route('/<int:property_id>/toggle_status', methods=('POST',))
def toggle_status(property_id):
    if 'user_id' not in session:
        flash('請先登入。', 'error')
        return redirect(url_for('auth.login'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT landlord_id, status FROM properties WHERE id = ?", (property_id,))
    prop = cursor.fetchone()
    
    if not prop:
        flash('找不到該房源！', 'error')
        return redirect(url_for('auth.profile'))
        
    if prop['landlord_id'] != session['user_id']:
        flash('您無權操作此房源。', 'error')
        return redirect(url_for('auth.profile'))
        
    new_status = 'inactive' if prop['status'] == 'active' else 'active'
    cursor.execute("UPDATE properties SET status = ? WHERE id = ?", (new_status, property_id))
    db.commit()
    
    status_text = '已標記為：已租出/已下架（首頁將不予顯示）' if new_status == 'inactive' else '已標記為：待租/刊登中（已於首頁公開顯示）'
    flash(f'🎉 房源狀態更新成功！{status_text}', 'success')
    return redirect(url_for('auth.profile'))

