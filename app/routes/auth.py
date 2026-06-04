import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models.user import User, Verification
from app.models import get_db


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
        owner_name = request.form.get('owner_name', '').strip()
        property_address = request.form.get('property_address', '').strip()
        
        if not id_card or not title_deed or not owner_name or not property_address:
            flash('請填寫所有欄位並上傳身分證與權狀影本', 'error')
            return redirect(url_for('auth.upload_docs'))
            
        # Get landlord's registered name from DB
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT name FROM users WHERE id = ?", (session['user_id'],))
        landlord_name = cursor.fetchone()['name']
        
        # Trigger AI automated deed verification (F-04 AI Upgrade)
        from app.utils.ai_verifier import ai_verify_deed
        status, score, ai_report = ai_verify_deed(landlord_name, owner_name, property_address)
        
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
        
        # Create verification with AI result
        Verification.create(
            user_id=session['user_id'],
            id_card_path=db_id_path,
            title_deed_path=db_deed_path,
            owner_name=owner_name,
            property_address=property_address,
            status=status,
            ai_report=ai_report
        )
        
        if status == 'approved':
            flash('🎉 AI 智慧審核成功！成功於網際網路地籍公開資料庫完成交叉比對，地籍真實度極高，已自動核准您的房東身分！', 'success')
        else:
            flash('❌ AI 智慧審核退件：公開地籍檢索未通過或登記所有權人姓名不符。請至個人控制台查看詳細 AI 審核報告。', 'error')
            
        return redirect(url_for('auth.profile'))
        
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

@bp.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('auth.login'))
        
    db = get_db()
    cursor = db.cursor()
    
    # Refresh user info
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    # Update session name just in case
    session['user_name'] = user['name']
    
    my_properties = []
    my_roommates = []
    
    if user['role'] == 'landlord':
        cursor.execute("SELECT * FROM properties WHERE landlord_id = ?", (user['id'],))
        my_properties = cursor.fetchall()
    elif user['role'] == 'student':
        cursor.execute("SELECT * FROM roommate_posts WHERE author_id = ?", (user['id'],))
        my_roommates = cursor.fetchall()
        
    # Get landlord verification status if landlord
    verification = None
    if user['role'] == 'landlord':
        cursor.execute("SELECT * FROM verifications WHERE user_id = ? ORDER BY submitted_at DESC LIMIT 1", (user['id'],))
        verification = cursor.fetchone()
        
    return render_template('auth/profile.html', user=user, properties=my_properties, roommates=my_roommates, verification=verification)

@bp.route('/verify_school_email', methods=('POST',))
def verify_school_email():
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('auth.login'))
        
    school_email = request.form.get('school_email', '').strip()
    
    if not school_email:
        flash('請輸入信箱。', 'error')
        return redirect(url_for('auth.profile'))
        
    # Check if school email ends with fcu
    if not (school_email.endswith('@fcu.edu.tw') or school_email.endswith('@mail.fcu.edu.tw') or school_email.endswith('@o365.fcu.edu.tw')):
        flash('綁定失敗！請使用逢甲大學官方學術信箱格式 (@fcu.edu.tw 或 @mail.fcu.edu.tw)。', 'error')
        return redirect(url_for('auth.profile'))
        
    User.update_school_email(session['user_id'], school_email)
    flash('🎉 逢甲信箱認證成功！已成功解鎖室友揪團及留言權限。', 'success')
    return redirect(url_for('auth.profile'))

@bp.route('/update_demo_score', methods=('POST',))
def update_demo_score():
    if 'user_id' not in session:
        flash('請先登入', 'error')
        return redirect(url_for('auth.login'))
        
    action = request.form.get('action')
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT score FROM users WHERE id = ?", (session['user_id'],))
    current_score = cursor.fetchone()['score']
    
    if action == 'add':
        new_score = min(100, current_score + 5)
        flash('👍 模擬守信行為 (如：準時付租、維修快速)！信用積分 +5。', 'success')
    elif action == 'deduct':
        new_score = max(0, current_score - 25)
        flash('⚠️ 模擬惡意行為 (如：違約不理、破壞家具)！信用積分 -25。', 'error')
    else:
        new_score = current_score
        
    User.update_score(session['user_id'], new_score)
    return redirect(url_for('auth.profile'))

@bp.route('/update_profile', methods=('POST',))
def update_profile():
    if 'user_id' not in session:
        flash('請先登入。', 'error')
        return redirect(url_for('auth.login'))
        
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not name:
        flash('姓名為必填欄位。', 'error')
        return redirect(url_for('auth.profile'))
        
    User.update_profile(session['user_id'], name, phone)
    
    # Update session name just in case
    session['user_name'] = name
    
    flash('🎉 個人檔案已成功更新！', 'success')
    return redirect(url_for('auth.profile'))

