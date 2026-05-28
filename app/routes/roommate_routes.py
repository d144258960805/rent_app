from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.roommate_post import RoommatePostModel
from datetime import datetime

roommate_bp = Blueprint('roommate_bp', __name__, url_prefix='/roommates')

@roommate_bp.route('/')
def index():
    posts = RoommatePostModel.get_all()
    return render_template('roommates/index.html', posts=posts)

@roommate_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        title = request.form.get('title')
        content = request.form.get('content')

        if not student_id or not title or not content:
            flash('請填寫所有必填欄位 (學生ID, 標題, 內容)！', 'error')
            return render_template('roommates/create.html')

        data = {
            'student_id': student_id,
            'title': title,
            'content': content,
            'required_gender': request.form.get('required_gender', '不限'),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            RoommatePostModel.create(data)
            flash('貼文新增成功！', 'success')
            return redirect(url_for('roommate_bp.index'))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('roommates/create.html')

    return render_template('roommates/create.html')

@roommate_bp.route('/<int:post_id>')
def view(post_id):
    post = RoommatePostModel.get_by_id(post_id)
    if not post:
        flash('找不到該貼文！', 'error')
        return redirect(url_for('roommate_bp.index'))
    return render_template('roommates/view.html', post=post)

@roommate_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
def edit(post_id):
    post = RoommatePostModel.get_by_id(post_id)
    if not post:
        flash('找不到該貼文！', 'error')
        return redirect(url_for('roommate_bp.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('標題與內容為必填！', 'error')
            return render_template('roommates/edit.html', post=post)

        data = {
            'title': title,
            'content': content,
            'required_gender': request.form.get('required_gender', post['required_gender'])
        }
        
        try:
            RoommatePostModel.update(post_id, data)
            flash('貼文更新成功！', 'success')
            return redirect(url_for('roommate_bp.view', post_id=post_id))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('roommates/edit.html', post=post)

    return render_template('roommates/edit.html', post=post)

@roommate_bp.route('/<int:post_id>/delete', methods=['POST'])
def delete(post_id):
    try:
        RoommatePostModel.delete(post_id)
        flash('貼文已成功刪除！', 'success')
    except Exception as e:
        flash(f'刪除時發生錯誤: {str(e)}', 'error')
    return redirect(url_for('roommate_bp.index'))
