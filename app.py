import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Call init_db on startup
init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def room_detail():
    return render_template('room_detail.html')

@app.route('/api/reviews', methods=['POST'])
def upload_review():
    room_id = request.form.get('room_id', 1) # Default to room 1 for demo
    content = request.form.get('content', '').strip()
    
    if not content:
        return jsonify({'error': '請填寫評論內容'}), 400

    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({'error': '不支援的檔案格式，請上傳 PNG, JPG 或 GIF'}), 400
            
            filename = secure_filename(file.filename)
            # Add a timestamp or uuid to prevent filename collisions in production
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            # Storing the relative path for the frontend
            image_url = f"/static/uploads/{unique_filename}"

    # Insert into database
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reviews (room_id, content, image_url)
            VALUES (?, ?, ?)
        ''', (room_id, content, image_url))
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({'error': '資料庫儲存失敗', 'details': str(e)}), 500

    return jsonify({'message': '上傳成功！', 'image_url': image_url}), 200

if __name__ == '__main__':
    app.run(debug=True)
