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
    with open('schema.sql', 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# Call init_db on startup
init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/<int:room_id>')
def room_detail(room_id):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
        room = cursor.fetchone()
        conn.close()
    except Exception as e:
        return f"資料庫讀取錯誤: {str(e)}", 500
        
    if room is None:
        return "該房源不存在", 404
        
    room_dict = dict(room)
    room_dict['tags_list'] = [t.strip() for t in room_dict['tags'].split(',')] if room_dict['tags'] else []
    return render_template('room_detail.html', room=room_dict)

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    query_param = request.args.get('query', '').strip()
    room_type = request.args.get('type', '').strip()
    price_max = request.args.get('price_max', '', type=str)
    has_subsidy = request.args.get('has_subsidy', '').strip() # '1', '0' or empty

    sql = "SELECT * FROM rooms WHERE 1=1"
    params = []

    # Search keyword in title, address, description, or tags
    if query_param:
        clean_query = query_param.lstrip('#')
        sql += " AND (title LIKE ? OR address LIKE ? OR description LIKE ? OR tags LIKE ?)"
        like_str = f"%{clean_query}%"
        params.extend([like_str, like_str, like_str, like_str])

    # Filter by room type
    if room_type and room_type != '全部':
        sql += " AND type = ?"
        params.append(room_type)

    # Filter by max price
    if price_max and price_max.isdigit():
        sql += " AND price <= ?"
        params.append(int(price_max))

    # Filter by rent subsidy (0 or 1)
    if has_subsidy in ('0', '1'):
        sql += " AND has_subsidy = ?"
        params.append(int(has_subsidy))

    sql += " ORDER BY id ASC" # Keep default ordering for display

    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        rooms = []
        for row in rows:
            r = dict(row)
            r['tags_list'] = [t.strip() for t in r['tags'].split(',')] if r['tags'] else []
            rooms.append(r)
        conn.close()
    except Exception as e:
        return jsonify({'error': '資料庫讀取失敗', 'details': str(e)}), 500

    return jsonify(rooms), 200

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    room_id = request.args.get('room_id', 1, type=int)
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, room_id, content, image_url, created_at 
            FROM reviews 
            WHERE room_id = ? 
            ORDER BY created_at DESC
        ''', (room_id,))
        rows = cursor.fetchall()
        reviews = []
        for row in rows:
            reviews.append({
                'id': row['id'],
                'room_id': row['room_id'],
                'content': row['content'],
                'image_url': row['image_url'],
                'created_at': row['created_at']
            })
        conn.close()
    except Exception as e:
        return jsonify({'error': '資料庫讀取失敗', 'details': str(e)}), 500

    return jsonify(reviews), 200

@app.route('/api/reviews', methods=['POST'])
def upload_review():
    room_id = request.form.get('room_id', 1, type=int)
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
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
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

@app.route('/api/rooms', methods=['POST'])
def create_room():
    title = request.form.get('title', '').strip()
    address = request.form.get('address', '').strip()
    room_type = request.form.get('type', '').strip()
    price = request.form.get('price', '').strip()
    size = request.form.get('size', '').strip()
    has_subsidy = request.form.get('has_subsidy', '0').strip() # '1' or '0'
    tags = request.form.get('tags', '').strip() # comma separated tags
    description = request.form.get('description', '').strip()
    owner_name = request.form.get('owner_name', '').strip()
    owner_phone = request.form.get('owner_phone', '').strip()

    # Form Validation
    if not title:
        return jsonify({'error': '請填寫房源名稱'}), 400
    if not address:
        return jsonify({'error': '請填寫房源地址'}), 400
    if not room_type or room_type == '全部':
        return jsonify({'error': '請選擇正確的房型'}), 400
    if not price or not price.isdigit() or int(price) <= 0:
        return jsonify({'error': '請輸入正確的月租金金額'}), 400
    if not size:
        return jsonify({'error': '請輸入正確的坪數大小'}), 400
    try:
        size_val = float(size)
        if size_val <= 0:
            raise ValueError
    except ValueError:
        return jsonify({'error': '請輸入正確的坪數大小'}), 400
    if not owner_name:
        return jsonify({'error': '請填寫房東姓名'}), 400
    if not owner_phone:
        return jsonify({'error': '請填寫聯絡電話'}), 400

    # Image upload handling
    image_url = '/static/images/room_demo.png' # default image
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return jsonify({'error': '不支援的檔案格式，請上傳 PNG, JPG 或 GIF'}), 400
            
            filename = secure_filename(file.filename)
            import uuid
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            image_url = f"/static/uploads/{unique_filename}"

    # Normalize tags: split by comma, strip whitespace, join back with comma
    tags_list = []
    if tags:
        # Support both half-width and full-width commas
        raw_tags = tags.replace('，', ',').split(',')
        for t in raw_tags:
            cleaned = t.strip().lstrip('#')
            if cleaned:
                tags_list.append(cleaned)
    tags_str = ','.join(tags_list)

    # Convert values
    price_val = int(price)
    subsidy_val = 1 if has_subsidy == '1' else 0

    # Save to SQLite database
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rooms (title, address, type, price, size, has_subsidy, image_url, tags, description, owner_name, owner_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, address, room_type, price_val, size_val, subsidy_val, image_url, tags_str, description, owner_name, owner_phone))
        conn.commit()
        new_room_id = cursor.lastrowid
        conn.close()
    except Exception as e:
        return jsonify({'error': '資料庫儲存失敗', 'details': str(e)}), 500

    return jsonify({
        'message': '房源刊登成功！',
        'room_id': new_room_id
    }), 200
from flask import Flask, render_template, g
from app.models import close_db

def create_app(test_config=None):
    app = Flask('app', instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'rent_app.db'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
        
    # ensure upload folder exists
    upload_path = os.path.join(app.root_path, 'static', 'uploads')
    try:
        os.makedirs(upload_path)
    except OSError:
        pass

    app.teardown_appcontext(close_db)

    def init_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(app.config['DATABASE'])
            db.row_factory = sqlite3.Row
            
        with app.open_resource('../database/schema.sql', mode='rb') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()

        # 安全升級：確保 properties 表包含 image_path 欄位
        try:
            db.cursor().execute("ALTER TABLE properties ADD COLUMN image_path TEXT;")
            db.commit()
        except sqlite3.OperationalError:
            pass

        # 安全升級：確保 verifications 表包含 owner_name, property_address, ai_report 欄位
        for col in ["owner_name", "property_address", "ai_report"]:
            try:
                db.cursor().execute(f"ALTER TABLE verifications ADD COLUMN {col} TEXT;")
                db.commit()
            except sqlite3.OperationalError:
                pass

        # 安全升級：更名 student_id 到 author_id
        try:
            db.cursor().execute("ALTER TABLE roommate_posts RENAME COLUMN student_id TO author_id;")
            db.commit()
        except sqlite3.OperationalError:
            pass

        # 安全升級：確保 roommate_posts 表包含新增的期望條件欄位
        for col in ["room_type", "gender_preference", "lifestyle_rules"]:
            try:
                db.cursor().execute(f"ALTER TABLE roommate_posts ADD COLUMN {col} TEXT;")
                db.commit()
            except sqlite3.OperationalError:
                pass

    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes import auth, property, roommate
    app.register_blueprint(auth.bp)
    app.register_blueprint(property.bp)
    app.register_blueprint(roommate.bp)

    @app.route('/')
    def index():
        from app.models.property import Property, Tag
        from flask import request
        
        query = request.args.get('query', '').strip()
        rent_range = request.args.get('rent_range', '')
        room_type = request.args.get('room_type', '')
        size_range = request.args.get('size_range', '')
        subsidy_available = request.args.get('subsidy_available', '')
        selected_tag = request.args.get('tag', '')
        # 多標籤篩選（從 checkbox 取得多個值）
        selected_tags = request.args.getlist('tags')

        properties = Property.get_filtered(
            query=query,
            rent_range=rent_range,
            room_type=room_type,
            size_range=size_range,
            subsidy_available=subsidy_available,
            tag_name=selected_tag,
            tag_names=selected_tags if selected_tags else None
        )
        
        tags = Tag.get_all()
        grouped_tags, category_icons = Tag.get_grouped()
        return render_template(
            'index.html',
            properties=properties,
            tags=tags,
            grouped_tags=grouped_tags,
            category_icons=category_icons,
            query=query,
            rent_range=rent_range,
            room_type=room_type,
            size_range=size_range,
            subsidy_available=subsidy_available,
            selected_tag=selected_tag,
            selected_tags=selected_tags
        )

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
