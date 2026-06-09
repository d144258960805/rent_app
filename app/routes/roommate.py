# app/routes/roommate.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.roommate import RoommatePost
from app.models import get_db

bp = Blueprint('roommate', __name__, url_prefix='/roommate')

def school_email_verified_required(f):
    # Helper decorator is nice, but we can also just check in the route body for maximum flexibility.
    pass

@bp.route('/')
def list_posts():
    room_type = request.args.get('room_type', '').strip()
    gender_preference = request.args.get('gender_preference', '').strip()
    posts = RoommatePost.get_all(room_type=room_type, gender_preference=gender_preference)
    return render_template(
        'roommate/list.html', 
        posts=posts, 
        selected_room_type=room_type, 
        selected_gender=gender_preference
    )

@bp.route('/post', methods=('GET', 'POST'))
def post():
    if 'user_id' not in session:
        flash('請先登入後再發布徵室友公告。', 'error')
        return redirect(url_for('auth.login'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT school_email, role FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    # Restrict to verified student school emails
    school_email = user['school_email']
    if not school_email or not (school_email.endswith('@fcu.edu.tw') or school_email.endswith('@mail.fcu.edu.tw') or school_email.endswith('@o365.fcu.edu.tw')):
        flash('🔒 權限受限：此功能限逢甲大學信箱認證之學生使用，請先前往「個人控制台」完成逢甲信箱綁定！', 'error')
        return redirect(url_for('auth.profile'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        room_type = request.form.get('room_type', '').strip()
        gender_preference = request.form.get('gender_preference', '').strip()
        lifestyle_rules = request.form.get('lifestyle_rules', '').strip()
        
        error = None
        if not title or not content:
            error = '標題與內容為必填。'
        elif room_type not in ['分租套房', '整層住家']:
            error = '請選擇正確的房型。'
        elif gender_preference not in ['男生', '女生', '不限']:
            error = '請選擇正確的性別偏好。'
            
        if error is None:
            RoommatePost.create(
                session['user_id'], 
                title, 
                content, 
                room_type=room_type, 
                gender_preference=gender_preference, 
                lifestyle_rules=lifestyle_rules
            )
            flash('🎉 徵室友公告刊登成功！學弟妹們已可在看板看見您的消息。', 'success')
            return redirect(url_for('roommate.list_posts'))
            
        flash(error, 'error')
        
    return render_template('roommate/post.html')

@bp.route('/<int:post_id>')
def detail(post_id):
    post = RoommatePost.get_by_id(post_id)
    if not post:
        flash('找不到該揪團公告！', 'error')
        return redirect(url_for('roommate.list_posts'))
        
    comments = RoommatePost.get_comments(post_id)
    
    # Check if current user is fcu verified to let them reply
    is_verified = False
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT school_email FROM users WHERE id = ?", (session['user_id'],))
        u = cursor.fetchone()
        if u and u['school_email'] and (u['school_email'].endswith('@fcu.edu.tw') or u['school_email'].endswith('@mail.fcu.edu.tw') or u['school_email'].endswith('@o365.fcu.edu.tw')):
            is_verified = True
            
    return render_template('roommate/detail.html', post=post, comments=comments, is_verified=is_verified)

@bp.route('/<int:post_id>/comment', methods=('POST',))
def comment(post_id):
    if 'user_id' not in session:
        flash('請先登入。', 'error')
        return redirect(url_for('auth.login'))
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT school_email FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    school_email = user['school_email']
    if not school_email or not (school_email.endswith('@fcu.edu.tw') or school_email.endswith('@mail.fcu.edu.tw') or school_email.endswith('@o365.fcu.edu.tw')):
        flash('🔒 留言失敗：本討論板僅限通過逢甲信箱認證之學生參與討論！', 'error')
        return redirect(url_for('roommate.detail', post_id=post_id))
        
    content = request.form.get('content', '').strip()
    if not content:
        flash('留言內容不得為空。', 'error')
        return redirect(url_for('roommate.detail', post_id=post_id))
        
    RoommatePost.add_comment(post_id, session['user_id'], content)
    flash('💬 回覆成功！已在時間軸新增留言。', 'success')
    return redirect(url_for('roommate.detail', post_id=post_id))
