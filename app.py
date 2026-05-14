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

    with app.app_context():
        init_db()

    # Register blueprints
    from app.routes import auth, property
    app.register_blueprint(auth.bp)
    app.register_blueprint(property.bp)

    @app.route('/')
    def index():
        return render_template('layout.html', content="Welcome to Feng Chia Rental Platform MVP")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
