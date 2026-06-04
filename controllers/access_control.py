from controllers.auth_controller import Session

class AccessControl:
    # 積分門檻設定
    CREDIT_THRESHOLD = 80

    @staticmethod
    def check_access(view_instance, feature_name="此功能"):
        """
        檢查目前使用者的積分是否達到門檻。
        如果低於門檻 (例如 < 80)，則會呼叫 view_instance 的 lock_ui() 方法。
        回傳值: True 表示允許存取，False 表示拒絕存取。
        """
        user = Session.get_current_user()
        if not user:
            # 如果尚未登入，理論上不該觸發到這裡，但為了安全起見先回傳 False
            return False

        # 從 user dict 中取得積分 (預設如果沒有該欄位則給 100 分)
        credit_score = user.get('credit_score', 100)
        
        if credit_score < AccessControl.CREDIT_THRESHOLD:
            # 觸發 UI 鎖定
            warning_msg = (
                f"【權限受限】\n"
                f"您的信用積分 ({credit_score} 分) 低於門檻 ({AccessControl.CREDIT_THRESHOLD} 分)！\n"
                f"系統已限制您使用「{feature_name}」。\n"
                f"如有疑問請聯繫管理員。"
            )
            
            # 檢查傳入的 view_instance 是否有 lock_ui 這個方法
            if hasattr(view_instance, 'lock_ui') and callable(getattr(view_instance, 'lock_ui')):
                view_instance.lock_ui(warning_msg)
            else:
                print(f"Warning: {view_instance} 缺少 lock_ui() 方法，無法執行畫面鎖定。")
                
            return False
            
        return True
