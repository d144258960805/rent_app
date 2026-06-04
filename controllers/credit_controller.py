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
