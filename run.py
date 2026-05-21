"""
run.py — 開發伺服器入口點
執行方式：python run.py
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
