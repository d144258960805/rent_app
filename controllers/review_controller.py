from database.db import get_db_connection
from controllers.credit_controller import CreditController

class ReviewController:
    @staticmethod
    def get_properties_list():
        """獲取所有房源以供下拉選單選擇"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM properties ORDER BY title ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def submit_review(property_id, user_id, rating, comment, is_anonymous):
        """
        提交一筆新評論，並觸發信用評分加分 (+5 分)
        """
        if not property_id:
            return False, "請選擇要評論的房源。"
            
        if not rating or rating < 1 or rating > 5:
            return False, "請給予 1 到 5 星的評分。"

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 寫入 reviews 表格
            cursor.execute('''
                INSERT INTO reviews (property_id, user_id, rating, comment, is_anonymous)
                VALUES (?, ?, ?, ?, ?)
            ''', (property_id, user_id, int(rating), comment, 1 if is_anonymous else 0))
            
            conn.commit()
            conn.close()
            
            # 觸發加分機制
            credit_success, credit_msg = CreditController.trigger(user_id, "review_submitted")
            
            success_msg = "評論成功發表！"
            if credit_success:
                success_msg += f"\n{credit_msg}"
                
            return True, success_msg

        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
            return False, f"發表評論失敗: {str(e)}"
