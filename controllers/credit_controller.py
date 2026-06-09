from database.db import get_db_connection
from controllers.auth_controller import Session
from models.credit import CreditLog

class CreditController:
    # 整合兩個版本的信用增減規則與事件
    RULES = {
        "review_submitted": {"change": 5, "desc": "發布真實房源評論"},
        "landlord_verified": {"change": 20, "desc": "完成房東實名認證"},
        "roommate_posted": {"change": 3, "desc": "發布室友徵求貼文"},
        "lease_violation": {"change": -25, "desc": "惡意違約/被投訴成立"},
        
        # 相容舊版/其他事件
        "account_created": {"change": 50, "desc": "帳號建立"},
        "tenant_verified": {"change": 50, "desc": "學生身分驗證通過"},
        "rent_paid_on_time": {"change": 5, "desc": "準時繳交租金"},
        "maintenance_quick": {"change": 5, "desc": "快速處理維修需求"},
        "rent_delayed": {"change": -10, "desc": "遲繳租金"},
        "fake_property": {"change": -30, "desc": "刊登虛假房源"},
        "contract_breach_malicious": {"change": -50, "desc": "惡意違約"}
    }

    @staticmethod
    def get_score(user_id):
        """查詢使用者的總積分 (對應 db 欄位 credit_score)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT credit_score FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row['credit_score'] if row else 100

    @staticmethod
    def get_logs(user_id):
        """查詢使用者的積分紀錄 (回傳 CreditLog 物件)"""
        return CreditLog.get_logs_by_user(user_id)

    @staticmethod
    def trigger(user_id, event_type):
        """
        根據事件代碼觸發積分增減。
        同時寫入 credits 與 credit_logs 兩個歷史紀錄表格以求系統最大相容性，
        並更新 users 中的 credit_score。
        回傳 (success_bool, message_str)
        """
        if event_type not in CreditController.RULES:
            print(f"Warning: 未知的信用事件類型 '{event_type}'")
            return False, "未知的信用事件"

        change = CreditController.RULES[event_type]["change"]
        desc = CreditController.RULES[event_type]["desc"]

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 1. 取得使用者目前的分數
            cursor.execute("SELECT credit_score FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                conn.close()
                return False, "找不到對應的使用者"

            old_score = user["credit_score"]
            # 限制分數介於 0 到 100 之間
            new_score = max(0, min(100, old_score + change))

            # 2. 更新 users 表中的 credit_score
            cursor.execute("UPDATE users SET credit_score = ? WHERE id = ?", (new_score, user_id))

            # 3. 寫入 credits 變更紀錄日誌 (系統評分 reviewer_id 設為 1)
            cursor.execute('''
                INSERT INTO credits (target_user_id, reviewer_id, score_change, reason)
                VALUES (?, 1, ?, ?)
            ''', (user_id, change, desc))

            # 4. 寫入 credit_logs 表格
            cursor.execute('''
                INSERT INTO credit_logs (user_id, action_type, points, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, event_type, change, desc))

            conn.commit()

            # 5. 如果是目前登入的用戶，即時刷新 Session
            current_user = Session.get_current_user()
            if current_user and current_user["id"] == user_id:
                current_user["credit_score"] = new_score
                Session.login_user(current_user)

            return True, f"信用評分變更成功！分數調整：{change:+d} 分，目前分數：{new_score} 分。"
        except Exception as e:
            conn.rollback()
            return False, f"評分更新失敗: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_score_history(user_id):
        """取得指定用戶的信用變更紀錄清單 (從 credits 表讀取)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, u.username as reviewer_name 
            FROM credits c
            JOIN users u ON c.reviewer_id = u.id
            WHERE c.target_user_id = ?
            ORDER BY c.created_at DESC
        ''', (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def check_credit_limit(user_id):
        """檢查是否達到存取限制"""
        score = CreditController.get_score(user_id)
        return {
            "can_post_property": score >= 80,
            "can_book_visit": score >= 80,
            "is_blacklisted": score < 60
        }
