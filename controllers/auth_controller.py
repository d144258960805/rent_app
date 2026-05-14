import hashlib
from database.db import get_db_connection

class Session:
    """管理當前應用程式的登入狀態 (簡單的單例模式概念)"""
    _current_user = None

    @classmethod
    def login_user(cls, user_data):
        cls._current_user = dict(user_data)

    @classmethod
    def logout_user(cls):
        cls._current_user = None

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def is_logged_in(cls):
        return cls._current_user is not None


class AuthController:
    @staticmethod
    def hash_password(password: str) -> str:
        """使用 SHA-256 對密碼進行雜湊處理"""
        # 在實際產品中建議加入 salt (鹽)，這裡以基本的 SHA-256 為例
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def register(username, email, password, role):
        """處理註冊邏輯"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 檢查信箱是否已經被註冊
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone() is not None:
            conn.close()
            return False, "該 Email 已經被註冊過了。"

        # 2. 將密碼進行雜湊
        hashed_password = AuthController.hash_password(password)

        # 3. 寫入資料庫
        try:
            # 預設信用積分為 100，學生/房東預設實名認證狀態為 0 (未認證)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, hashed_password, role))
            conn.commit()
            return True, "註冊成功！"
        except Exception as e:
            conn.rollback()
            return False, f"發生錯誤: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def login(email, password):
        """處理登入邏輯"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 根據 email 尋找使用者
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        # 2. 驗證帳號是否存在
        if user is None:
            return False, "找不到該 Email 對應的帳號。"

        # 3. 驗證密碼雜湊是否吻合
        input_hash = AuthController.hash_password(password)
        if input_hash != user['password_hash']:
            return False, "密碼錯誤。"

        # 4. 登入成功，將使用者資訊存入 Session
        Session.login_user(user)
        return True, "登入成功！"

    @staticmethod
    def logout():
        """處理登出邏輯"""
        Session.logout_user()
        return True, "已成功登出。"
