from database.db import get_db_connection
from controllers.credit_controller import CreditController

class RoommateController:
    @staticmethod
    def get_all_posts():
        """獲取所有揪室友貼文，包含發文者的使用者名稱與信箱、信用積分"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.*, u.username, u.email, u.credit_score 
            FROM roommates r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.created_at DESC
        ''')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def create_post(user_id, title, description, expected_rent):
        """
        發布揪室友貼文。完成後可獲得信用積分加分 (+3 分)。
        """
        if not title or not description:
            return False, "貼文標題與內容描述均不能留空！"

        try:
            expected_rent_val = int(expected_rent) if expected_rent else 0
        except ValueError:
            return False, "預期租金必須是數字！"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO roommates (user_id, title, description, expected_rent)
                VALUES (?, ?, ?, ?)
            ''', (user_id, title, description, expected_rent_val))
            
            conn.commit()
            conn.close()

            # 觸發發文信用加分 (+3 分)
            credit_success, credit_msg = CreditController.trigger(user_id, "roommate_posted")
            
            success_msg = "徵室友貼文發表成功！"
            if credit_success:
                success_msg += f"\n{credit_msg}"

            return True, success_msg
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return False, f"發布貼文失敗: {str(e)}"

    @staticmethod
    def delete_post(post_id, user_id):
        """刪除貼文 (限發文者本人可刪除)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. 檢查是否為本人
            cursor.execute("SELECT user_id FROM roommates WHERE id = ?", (post_id,))
            post = cursor.fetchone()
            if not post:
                conn.close()
                return False, "找不到該貼文。"
                
            if post["user_id"] != user_id:
                conn.close()
                return False, "您沒有權限刪除他人的貼文！"

            # 2. 進行刪除
            cursor.execute("DELETE FROM roommates WHERE id = ?", (post_id,))
            conn.commit()
            conn.close()
            return True, "貼文已成功刪除。"
        except Exception as e:
            if conn:
                conn.close()
            return False, f"刪除失敗: {str(e)}"
