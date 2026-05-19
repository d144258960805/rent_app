from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.review import ReviewModel
from datetime import datetime

review_bp = Blueprint('review_bp', __name__, url_prefix='/reviews')

@review_bp.route('/')
def index():
    reviews = ReviewModel.get_all()
    return render_template('reviews/index.html', reviews=reviews)

@review_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        property_id = request.form.get('property_id')
        student_id = request.form.get('student_id')
        content = request.form.get('content')

        if not property_id or not student_id or not content:
            flash('請填寫所有必填欄位 (房源ID, 學生ID, 內容)！', 'error')
            return render_template('reviews/create.html')

        data = {
            'property_id': property_id,
            'student_id': student_id,
            'content': content,
            'image_url': request.form.get('image_url', ''),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            ReviewModel.create(data)
            flash('新增評論成功！', 'success')
            return redirect(url_for('review_bp.index'))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('reviews/create.html')

    return render_template('reviews/create.html')

@review_bp.route('/<int:review_id>')
def view(review_id):
    review = ReviewModel.get_by_id(review_id)
    if not review:
        flash('找不到該評論！', 'error')
        return redirect(url_for('review_bp.index'))
    return render_template('reviews/view.html', review=review)

@review_bp.route('/<int:review_id>/edit', methods=['GET', 'POST'])
def edit(review_id):
    review = ReviewModel.get_by_id(review_id)
    if not review:
        flash('找不到該評論！', 'error')
        return redirect(url_for('review_bp.index'))

    if request.method == 'POST':
        content = request.form.get('content')
        
        if not content:
            flash('評論內容為必填！', 'error')
            return render_template('reviews/edit.html', review=review)

        data = {
            'content': content,
            'image_url': request.form.get('image_url', review['image_url'])
        }
        
        try:
            ReviewModel.update(review_id, data)
            flash('評論更新成功！', 'success')
            return redirect(url_for('review_bp.view', review_id=review_id))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('reviews/edit.html', review=review)

    return render_template('reviews/edit.html', review=review)

@review_bp.route('/<int:review_id>/delete', methods=['POST'])
def delete(review_id):
    try:
        ReviewModel.delete(review_id)
        flash('評論已成功刪除！', 'success')
    except Exception as e:
        flash(f'刪除時發生錯誤: {str(e)}', 'error')
    return redirect(url_for('review_bp.index'))
