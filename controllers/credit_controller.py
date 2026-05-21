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
