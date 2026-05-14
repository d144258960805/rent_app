from functools import wraps
from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models.user import User
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

@bp.route('/post')
@landlord_verified_required
def post():
    return render_template('property/post.html')
