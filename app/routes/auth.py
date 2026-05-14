import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models.user import User, Verification

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        role = request.form['role']
        
        error = None
        if not email or not password or not name or not role:
            error = '所有欄位皆為必填。'
            
        if error is None:
            existing_user = User.get_by_email(email)
            if existing_user is None:
                User.create(email, generate_password_hash(password), name, role)
                flash('註冊成功，請登入', 'success')
                return redirect(url_for('auth.login'))
            else:
                error = '此 Email 已被註冊。'
                
        flash(error, 'error')
        
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        
        user = User.get_by_email(email)
        
        if user is None:
            error = '帳號不存在。'
        elif not check_password_hash(user['password_hash'], password):
            error = '密碼錯誤。'
            
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            session['user_name'] = user['name']
            flash('登入成功', 'success')
            return redirect(url_for('index'))
            
        flash(error, 'error')
        
    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash('已登出', 'success')
    return redirect(url_for('index'))

@bp.route('/upload_docs', methods=('GET', 'POST'))
def upload_docs():
    if 'user_id' not in session or session.get('user_role') != 'landlord':
        flash('只有房東可以上傳證明文件', 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        id_card = request.files.get('id_card')
        title_deed = request.files.get('title_deed')
        
        if not id_card or not title_deed:
            flash('請同時上傳身分證與權狀影本', 'error')
            return redirect(url_for('auth.upload_docs'))
            
        id_card_filename = secure_filename(id_card.filename)
        title_deed_filename = secure_filename(title_deed.filename)
        
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        id_card_path = os.path.join(upload_folder, f"{session['user_id']}_id_{id_card_filename}")
        title_deed_path = os.path.join(upload_folder, f"{session['user_id']}_deed_{title_deed_filename}")
        
        id_card.save(id_card_path)
        title_deed.save(title_deed_path)
        
        # Save relative paths to DB
        db_id_path = f"uploads/{session['user_id']}_id_{id_card_filename}"
        db_deed_path = f"uploads/{session['user_id']}_deed_{title_deed_filename}"
        
        Verification.create(session['user_id'], db_id_path, db_deed_path)
        
        flash('文件上傳成功，請等待系統管理員審核。', 'success')
        return redirect(url_for('index'))
        
    return render_template('auth/upload_docs.html')

@bp.route('/admin_review', methods=('GET', 'POST'))
def admin_review():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        flash('無權限訪問', 'error')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        verification_id = request.form['verification_id']
        action = request.form['action'] # 'approve' or 'reject'
        status = 'approved' if action == 'approve' else 'rejected'
        
        Verification.update_status(verification_id, status, session['user_id'])
        flash(f'審核已完成: {status}', 'success')
        return redirect(url_for('auth.admin_review'))
        
    pending_verifications = Verification.get_pending()
    return render_template('auth/admin_review.html', verifications=pending_verifications)
