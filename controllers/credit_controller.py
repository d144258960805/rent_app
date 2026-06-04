from database.db import get_db_connection
from controllers.auth_controller import Session

class CreditController:
    # 積分增減規則定義
    RULES = {
        "review_submitted": {"change": 5, "desc": "發布真實房源評論"},
        "landlord_verified": {"change": 20, "desc": "完成房東實名認證"},
        "roommate_posted": {"change": 3, "desc": "發布室友徵求貼文"},
        "lease_violation": {"change": -25, "desc": "惡意違約/被投訴成立"}
    }

    @staticmethod
    def trigger(user_id, event_type):
        """
        觸發信用事件，調整分數並記錄歷程。
        如果修改的是目前登入的用戶，會同步刷新其 Session 中的 credit_score 狀態。
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

            # 3. 寫入 credits 變更紀錄日誌
            # 這裡系統評分設定 reviewer_id = 1 (管理員/系統)
            cursor.execute('''
                INSERT INTO credits (target_user_id, reviewer_id, score_change, reason)
                VALUES (?, 1, ?, ?)
            ''', (user_id, change, desc))

            conn.commit()

            # 4. 如果是目前登入的用戶，即時刷新 Session
            current_user = Session.get_current_user()
            if current_user and current_user["id"] == user_id:
                current_user["credit_score"] = new_score
                # 重新保存回去
                Session.login_user(current_user)

            return True, f"信用評分變更成功！分數調整：{change:+d} 分，目前分數：{new_score} 分。"
        except Exception as e:
            conn.rollback()
            return False, f"評分更新失敗: {str(e)}"
        finally:
            conn.close()

    @staticmethod
    def get_score_history(user_id):
        """取得指定用戶的信用變更紀錄清單"""
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
from database.db import get_connection
from models.credit import CreditLog

# 積分事件定義表
CREDIT_EVENTS = {
    "account_created": {"points": 50, "desc": "帳號建立"},
    "landlord_verified": {"points": 50, "desc": "房東身分驗證通過"},
    "tenant_verified": {"points": 50, "desc": "學生身分驗證通過"},
    "rent_paid_on_time": {"points": 5, "desc": "準時繳交租金"},
    "maintenance_quick": {"points": 5, "desc": "快速處理維修需求"},
    "review_submitted": {"points": 2, "desc": "發表優質評論"},
    "rent_delayed": {"points": -10, "desc": "遲繳租金"},
    "fake_property": {"points": -30, "desc": "刊登虛假房源"},
    "contract_breach_malicious": {"points": -50, "desc": "惡意違約"}
}

class CreditController:
    @staticmethod
    def get_score(user_id):
        """查詢使用者的總積分"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT total_credit FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row['total_credit'] if row else 0

    @staticmethod
    def get_logs(user_id):
        """查詢使用者的積分紀錄"""
        return CreditLog.get_logs_by_user(user_id)

    @staticmethod
    def add_score(user_id, points):
        """手動增加/扣除積分，並更新總分"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET total_credit = total_credit + ? WHERE id = ?", (points, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def trigger(user_id, event_key):
        """
        根據事件代碼觸發積分增減
        回傳: (更新後的總分, 紀錄的描述字串)
        """
        if event_key not in CREDIT_EVENTS:
            raise ValueError(f"未知的積分事件: {event_key}")
            
        event = CREDIT_EVENTS[event_key]
        points = event["points"]
        desc = event["desc"]
        
        # 1. 記錄 Log
        CreditLog.add_log(user_id, event_key, points, desc)
        
        # 2. 更新 users 總分
        CreditController.add_score(user_id, points)
        
        # 3. 回傳最新總分
        current_score = CreditController.get_score(user_id)
        return current_score, desc

    @staticmethod
    def check_credit_limit(user_id):
        """檢查是否達到存取限制"""
        score = CreditController.get_score(user_id)
        return {
            "can_post_property": score >= 80,
            "can_book_visit": score >= 80,
            "is_blacklisted": score < 60
        }
