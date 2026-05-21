import os
import sqlite3
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
            
        with app.open_resource('../database/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
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

        properties = Property.get_filtered(
            query=query,
            rent_range=rent_range,
            room_type=room_type,
            size_range=size_range,
            subsidy_available=subsidy_available,
            tag_name=selected_tag
        )
        
        tags = Tag.get_all()
        return render_template(
            'index.html',
            properties=properties,
            tags=tags,
            query=query,
            rent_range=rent_range,
            room_type=room_type,
            size_range=size_range,
            subsidy_available=subsidy_available,
            selected_tag=selected_tag
        )

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
