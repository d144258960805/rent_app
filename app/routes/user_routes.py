from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.models.user import UserModel
from datetime import datetime

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')

@user_bp.route('/')
def index():
    users = UserModel.get_all()
    return render_template('users/index.html', users=users)

@user_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')

        if not email or not password or not name or not role:
            flash('請填寫所有必填欄位 (信箱, 密碼, 姓名, 角色)！', 'error')
            return render_template('users/create.html')

        data = {
            'email': email,
            'password_hash': password, # 實際應用應進行 hash 處理
            'name': name,
            'role': role,
            'phone': request.form.get('phone', ''),
            'points': 100,
            'is_verified': False,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            UserModel.create(data)
            flash('新增使用者成功！', 'success')
            return redirect(url_for('user_bp.index'))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('users/create.html')

    return render_template('users/create.html')

@user_bp.route('/<int:user_id>')
def view(user_id):
    user = UserModel.get_by_id(user_id)
    if not user:
        flash('找不到該使用者！', 'error')
        return redirect(url_for('user_bp.index'))
    return render_template('users/view.html', user=user)

@user_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit(user_id):
    user = UserModel.get_by_id(user_id)
    if not user:
        flash('找不到該使用者！', 'error')
        return redirect(url_for('user_bp.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        
        if not email or not name:
            flash('信箱與姓名為必填！', 'error')
            return render_template('users/edit.html', user=user)

        data = {
            'email': email,
            'name': name,
            'phone': request.form.get('phone', ''),
            'role': request.form.get('role', user['role'])
        }
        
        try:
            UserModel.update(user_id, data)
            flash('使用者更新成功！', 'success')
            return redirect(url_for('user_bp.view', user_id=user_id))
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')
            return render_template('users/edit.html', user=user)

    return render_template('users/edit.html', user=user)

@user_bp.route('/<int:user_id>/delete', methods=['POST'])
def delete(user_id):
    try:
        UserModel.delete(user_id)
        flash('使用者已成功刪除！', 'success')
    except Exception as e:
        flash(f'刪除時發生錯誤: {str(e)}', 'error')
    return redirect(url_for('user_bp.index'))
