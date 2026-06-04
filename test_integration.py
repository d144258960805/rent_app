import os
import sys
import unittest
from database.db import init_db, get_db_connection
from controllers.auth_controller import AuthController, Session
from controllers.filter_controller import FilterController
from controllers.search_controller import SearchController
from controllers.review_controller import ReviewController
from controllers.verify_controller import VerifyController
from controllers.credit_controller import CreditController
from controllers.roommate_controller import RoommateController
from controllers.access_control import AccessControl

class TestFengChiaRentalPlatform(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """在所有測試開始前，動態初始化資料庫，調整初始分數以測試加分"""
        print("\n=== START INITIALIZE DATABASE ===")
        init_db()
        
        # 注入乾淨的測試初始帳號
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM properties")
        cursor.execute("DELETE FROM reviews")
        cursor.execute("DELETE FROM credits")
        cursor.execute("DELETE FROM roommates")
        
        cls.landlord_email = "test_landlord@fcu.edu.tw"
        cls.student_email = "test_student@o365.fcu.edu.tw"
        cls.pwd = "test1234"
        
        # 1. 註冊測試房東並取得其動態 ID (初始分數設為 80，以測試加 20 分後達 100 分)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_verified, credit_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("Test Landlord", cls.landlord_email, AuthController.hash_password(cls.pwd), "landlord", 0, 80))
        cls.landlord_id = cursor.lastrowid
        
        # 2. 註冊測試學生並取得其動態 ID (初始分數設為 90，以測試加 5 分後達 95 分)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_verified, credit_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("Test Student", cls.student_email, AuthController.hash_password(cls.pwd), "student", 1, 90))
        cls.student_id = cursor.lastrowid
        
        # 3. 建立測試房源並取得其動態 ID (由該房東刊登)
        cursor.execute('''
            INSERT INTO properties (landlord_id, title, description, rent, room_type, size, has_subsidy, tags, address, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cls.landlord_id, "Wenhua Rd. Big Suite", "Very comfortable suite", 8500, "獨立套房", 8.5, 1, "落地窗,採光好,養寵物", "Wenhua Rd. No. 120", 24.179, 120.647))
        cls.property_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        print(f"=== TEST DATABASE PREPARED (Landlord ID: {cls.landlord_id}, Student ID: {cls.student_id}, Property ID: {cls.property_id}) ===\n")

    def test_01_auth_flow(self):
        """測試註冊與登入流程"""
        print("[RUN] Testing Register and Login Verification...")
        # 測試正常學生登入
        success, msg = AuthController.login(self.student_email, self.pwd)
        self.assertTrue(success, "Student login should succeed")
        self.assertEqual(Session.get_current_user()["username"], "Test Student")
        print("  => [SUCCESS] Password hashing and Session storage function perfectly.")

    def test_02_filter_flow(self):
        """測試分類篩選 (F-01)"""
        print("[RUN] Testing Property Filtering (F-01)...")
        # 篩選月租 9000 以下、獨立套房、可租補
        results = FilterController.filter_properties(max_rent=9000, room_type="獨立套房", has_subsidy=True)
        self.assertEqual(len(results), 1, "Should filter 1 matched property")
        self.assertEqual(results[0]["title"], "Wenhua Rd. Big Suite")
        print("  => [SUCCESS] Rent, room type and subsidy filter functions perfectly.")

    def test_03_search_flow(self):
        """測試標籤關鍵字搜尋 (F-02)"""
        print("[RUN] Testing Keyword and Tag Search (F-02)...")
        # 疊加搜尋標籤：養寵物、採光好
        results = SearchController.search_properties(keyword="Wenhua", active_tags=["養寵物", "採光好"])
        self.assertEqual(len(results), 1, "Should match keywords and tags")
        
        # 測試找不到的關鍵字
        results_empty = SearchController.search_properties(keyword="Taipei")
        self.assertEqual(len(results_empty), 0, "Should find no matches")
        print("  => [SUCCESS] Multi-tag combinations and keyword wildcard search query works perfectly.")

    def test_04_review_and_credit_reward(self):
        """測試評論上傳與信用分數加分 (F-03 & F-05)"""
        print("[RUN] Testing Student Review Submission & Credit Points Addition (F-03 & F-05)...")
        # 確保登入學生
        AuthController.login(self.student_email, self.pwd)
        user = Session.get_current_user()
        
        # 提交評論至房源
        success, msg = ReviewController.submit_review(
            property_id=self.property_id, 
            user_id=user["id"], 
            rating=5, 
            comment="Awesome landlord!", 
            is_anonymous=False
        )
        self.assertTrue(success, "Submit review should succeed")
        
        # 驗證評論是否寫入資料庫
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT comment FROM reviews WHERE property_id = ?", (self.property_id,))
        review = cursor.fetchone()
        self.assertIsNotNone(review)
        self.assertEqual(review["comment"], "Awesome landlord!")
        
        # 驗證信用分數是否獲得加分 (90 + 5 = 95 分)
        cursor.execute("SELECT credit_score FROM users WHERE email = ?", (self.student_email,))
        updated_score = cursor.fetchone()["credit_score"]
        self.assertEqual(updated_score, 95, "Student should get +5 credit points")
        
        # 驗證 Session 狀態是否即時同步更新
        self.assertEqual(Session.get_current_user()["credit_score"], 95, "Session score should update to 95")
        
        conn.close()
        print("  => [SUCCESS] Review successfully saved, credit score rewarded +5, and session refreshed!")

    def test_05_landlord_verification_flow(self):
        """測試房東文件驗證與管理員核准 (F-04)"""
        print("[RUN] Testing Landlord Document Verification and Admin Approval (F-04)...")
        # 1. 模擬房東提交文件
        success, msg = VerifyController.submit_verification(user_id=self.landlord_id, id_card_path="main.py", property_deed_path="main.py")
        self.assertTrue(success, "Landlord verification upload should succeed")
        
        # 2. 檢查資料庫狀態是否改為 2 (審核中)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_verified FROM users WHERE id = ?", (self.landlord_id,))
        self.assertEqual(cursor.fetchone()["is_verified"], 2, "Status should update to Pending (2)")
        
        # 3. 管理員獲取審核清單
        pending = VerifyController.get_pending_landlords()
        self.assertEqual(len(pending), 1, "Admin pending list should contain 1 item")
        self.assertEqual(pending[0]["username"], "Test Landlord")
        
        # 4. 管理員核准通過
        success, msg = VerifyController.approve_landlord(landlord_id=self.landlord_id)
        self.assertTrue(success, "Admin approval should succeed")
        
        # 5. 驗證房東狀態是否改為 1 (已驗證)，且獲得信用加分 (80 + 20 = 100 分)
        cursor.execute("SELECT is_verified, credit_score FROM users WHERE id = ?", (self.landlord_id,))
        row = cursor.fetchone()
        self.assertEqual(row["is_verified"], 1, "Status should update to Approved (1)")
        self.assertEqual(row["credit_score"], 100, "Approved landlord should get +20 credit points")
        
        conn.close()
        print("  => [SUCCESS] Landlord verification three-state workflow and admin rewards executed perfectly.")

    def test_06_roommate_post_flow(self):
        """測試揪室友貼文發布與防權限越級刪除 (F-06)"""
        print("[RUN] Testing Roommate Matchmaking & Ownership Deletion Verification (F-06)...")
        # 1. 測試學生甲發文
        success, msg = RoommateController.create_post(user_id=self.student_id, title="Wenhua roommate", description="No bad habits", expected_rent="5500")
        self.assertTrue(success, "Create roommate post should succeed")
        
        # 2. 檢索貼文
        posts = RoommateController.get_all_posts()
        self.assertEqual(len(posts), 1)
        post_id = posts[0]["id"]
        
        # 3. 測試越權刪除 (房東 id 企圖刪除學生的貼文)
        success_del, msg_del = RoommateController.delete_post(post_id=post_id, user_id=self.landlord_id)
        self.assertFalse(success_del, "Ownership verification should block deletion")
        
        # 4. 測試本人安全刪除
        success_del, msg_del = RoommateController.delete_post(post_id=post_id, user_id=self.student_id)
        self.assertTrue(success_del, "Owner should be allowed to delete own post")
        print("  => [SUCCESS] Roommate posting and security block on foreign deletion works perfectly.")

    def test_07_access_control_limits(self):
        """測試信用低於 80 門檻功能限制 (F-07)"""
        print("[RUN] Testing Credit Score Restriction limits (F-07)...")
        
        # 建立一個測試用 Dummy View (模擬 UI)
        class DummyView:
            def __init__(self):
                self.is_locked = False
                self.lock_message = ""
            def lock_ui(self, msg):
                self.is_locked = True
                self.lock_message = msg

        view_instance = DummyView()
        
        # 1. 當分數為 105 分時，應被允許存取
        current_user = Session.get_current_user()
        current_user["credit_score"] = 105
        Session.login_user(current_user)
        
        allowed = AccessControl.check_access(view_instance, "發貼文")
        self.assertTrue(allowed, "Access should be allowed with high score")
        self.assertFalse(view_instance.is_locked, "UI should not be locked")
        
        # 2. 當分數為 75 分時，應被拒絕存取，且觸發 lock_ui
        current_user["credit_score"] = 75
        Session.login_user(current_user)
        
        allowed = AccessControl.check_access(view_instance, "發貼文")
        self.assertFalse(allowed, "Access should be blocked with low score")
        self.assertTrue(view_instance.is_locked, "UI should be locked")
        self.assertIn("75", view_instance.lock_message, "Should display correct warning message")
        print("  => [SUCCESS] AccessControl successfully locks UI when score drops below 80.")

if __name__ == "__main__":
    unittest.main()
