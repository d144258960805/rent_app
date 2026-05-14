import customtkinter as ctk

class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 標題
        title_label = ctk.CTkLabel(self, text="首頁 (Home)", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # 導覽區塊
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=20)
        
        buttons = [
            ("條件篩選 (Filter)", "FilterFrame"),
            ("標籤搜尋 (Search)", "SearchFrame"),
            ("撰寫評論 (Review)", "ReviewFrame"),
            ("房東驗證 (Verify)", "VerifyFrame"),
            ("信用評分 (Credit)", "CreditFrame"),
            ("揪室友區 (Roommate)", "RoommateFrame"),
        ]
        
        for text, frame_name in buttons:
            btn = ctk.CTkButton(
                nav_frame, 
                text=text, 
                command=lambda f=frame_name: self.controller.show_frame(f),
                width=200
            )
            btn.pack(pady=10)
            
        # 登出按鈕
        logout_btn = ctk.CTkButton(
            self, 
            text="登出", 
            fg_color="#D35B58", 
            hover_color="#C75050",
            command=self.logout
        )
        logout_btn.pack(side="bottom", pady=20)

    def logout(self):
        from controllers.auth_controller import AuthController
        AuthController.logout()
        self.controller.show_frame("LoginFrame")
