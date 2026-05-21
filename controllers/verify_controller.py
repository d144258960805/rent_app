import shutil
import os
from database.db import get_db_connection
from controllers.auth_controller import Session
from controllers.credit_controller import CreditController

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "assets", "uploads")

class VerifyController:
    @staticmethod
    def ensure_upload_dir():
        """確保上傳目錄存在"""
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

    @staticmethod
    def submit_verification(user_id, id_card_path, property_deed_path):
        """
        提交房東驗證申請。將 is_verified 改為 2 (審核中)，並把相關檔案複製至 assets/uploads/
        """
        if not id_card_path or not property_deed_path:
            return False, "身分證件與房屋產權證明均必須上傳！"

        VerifyController.ensure_upload_dir()

        try:
            # 複製檔案至上傳資料夾
            id_ext = os.path.splitext(id_card_path)[1]
            deed_ext = os.path.splitext(property_deed_path)[1]
            
            new_id_path = os.path.join(UPLOAD_DIR, f"landlord_{user_id}_id{id_ext}")
            new_deed_path = os.path.join(UPLOAD_DIR, f"landlord_{user_id}_deed{deed_ext}")
            
            shutil.copy(id_card_path, new_id_path)
            shutil.copy(property_deed_path, new_deed_path)

            # 更新資料庫中的狀態為 2 (審核中)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_verified = 2 WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()

            # 即時更新當前使用者 session
            curr_user = Session.get_current_user()
            if curr_user and curr_user["id"] == user_id:
                curr_user["is_verified"] = 2
                Session.login_user(curr_user)

            return True, "驗證文件上傳成功，等待管理員審核！"
        except Exception as e:
            return False, f"上傳過程中發生錯誤: {str(e)}"

    @staticmethod
    def get_pending_landlords():
        """取得所有審核中的房東清單"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, created_at FROM users WHERE role = 'landlord' AND is_verified = 2")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def approve_landlord(landlord_id):
        """核准房東身分：is_verified 設為 1，並發起信用評分獎勵"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE users SET is_verified = 1 WHERE id = ?", (landlord_id,))
            conn.commit()
            conn.close()

            # 核准通過，獲得信用加分 (+20 分)
            CreditController.trigger(landlord_id, "landlord_verified")
            
            # 如果目前是該房東登入，更新其狀態
            curr_user = Session.get_current_user()
            if curr_user and curr_user["id"] == landlord_id:
                curr_user["is_verified"] = 1
                Session.login_user(curr_user)

            return True, "已成功核准該房東驗證！"
        except Exception as e:
            if conn:
                conn.close()
            return False, f"核准失敗: {str(e)}"

    @staticmethod
    def reject_landlord(landlord_id):
        """拒絕房東身分：is_verified 重設為 0"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("UPDATE users SET is_verified = 0 WHERE id = ?", (landlord_id,))
            conn.commit()
            conn.close()

            # 如果目前是該房東登入，更新其狀態
            curr_user = Session.get_current_user()
            if curr_user and curr_user["id"] == landlord_id:
                curr_user["is_verified"] = 0
                Session.login_user(curr_user)

            return True, "已拒絕該房東的驗證申請。"
        except Exception as e:
            if conn:
                conn.close()
            return False, f"操作失敗: {str(e)}"
