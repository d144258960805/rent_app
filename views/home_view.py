import customtkinter as ctk
from database.db import get_db_connection
from controllers.auth_controller import Session
from components.property_card import PropertyCard

class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 使用雙欄版面：左側為全系統房源清單 (佔主要空間)，右側為個人狀態面板與導覽
        self.grid_columnconfigure(0, weight=2)  # 左側房源 (大)
        self.grid_columnconfigure(1, weight=1)  # 右側面板 (小)
        self.grid_rowconfigure(0, weight=1)

        # ================= 左欄：全系統最新房源清單 =================
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        lbl_head = ctk.CTkLabel(left_panel, text="🏠 逢甲校園最新精選房源", font=ctk.CTkFont(size=22, weight="bold"), anchor="w")
        lbl_head.pack(fill="x", pady=(0, 10))
        
        self.scroll_properties = ctk.CTkScrollableFrame(left_panel)
        self.scroll_properties.pack(fill="both", expand=True)

        # ================= 右欄：個人狀態與導覽面板 =================
        self.right_panel = ctk.CTkFrame(self, width=280)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.right_panel.pack_propagate(False)

        # 這部分會在 tkraise 中動態渲染以即時更新用戶積分與狀態
        self.user_card = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.user_card.pack(fill="both", expand=True, pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_all_properties()
        self.render_user_panel()

    def load_all_properties(self):
        """從資料庫加載所有的房源並顯示於左側清單"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM properties ORDER BY created_at DESC")
        properties = cursor.fetchall()
        conn.close()

        # 清除舊的房源卡片
        for widget in self.scroll_properties.winfo_children():
            widget.destroy()

        if not properties:
            no_lbl = ctk.CTkLabel(
                self.scroll_properties, 
                text="暫無任何已刊登的房源資料。", 
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color="gray"
            )
            no_lbl.pack(pady=50)
            return

        # 渲染每一個房源卡片
        for prop in properties:
            card = PropertyCard(self.scroll_properties, dict(prop), self.controller)
            card.pack(fill="x", padx=10, pady=8)

    def render_user_panel(self):
        """動態加載當前登入者資訊，包括姓名、角色、以及信用評分"""
        # 清除舊元件
        for widget in self.user_card.winfo_children():
            widget.destroy()

        user = Session.get_current_user()
        if not user:
            return

        # 1. 歡迎標題與角色
        role_map = {"student": "學生租客", "landlord": "認證房東", "admin": "系統管理員"}
        role_display = role_map.get(user["role"], "平台會員")
        
        lbl_welcome = ctk.CTkLabel(
            self.user_card, 
            text=f"歡迎回來，{user['username']} 👋", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl_welcome.pack(pady=(15, 2))
        
        lbl_role = ctk.CTkLabel(
            self.user_card, 
            text=f"【{role_display}】", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        lbl_role.pack(pady=(0, 15))

        # 2. 信用分數預覽小板
        score = user.get("credit_score", 100)
        if score >= 80:
            status_color = ("#28A745", "#34C759")
        else:
            status_color = ("#D35B58", "#FF453A")
            
        score_box = ctk.CTkFrame(self.user_card, fg_color=("#F2F2F7", "#1C1C1E"), corner_radius=8)
        score_box.pack(fill="x", padx=20, pady=(0, 20), ipady=8)
        
        score_title = ctk.CTkLabel(score_box, text="您的信用評分", font=ctk.CTkFont(size=11), text_color="gray")
        score_title.pack()
        
        score_val = ctk.CTkLabel(score_box, text=f"{score} 分", font=ctk.CTkFont(size=22, weight="bold"), text_color=status_color)
        score_val.pack()

        # 3. 系統導覽按鈕區
        nav_lbl = ctk.CTkLabel(self.user_card, text="系統功能導覽", font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
        nav_lbl.pack(fill="x", padx=20, pady=(0, 5))

        buttons = [
            ("🔍 條件分類篩選", "FilterFrame"),
            ("🏷️ 標籤關鍵字搜尋", "SearchFrame"),
            ("🤝 揪團徵室友區", "RoommateFrame"),
            ("🛡️ 房東身份驗證", "VerifyFrame"),
            ("⚖️ 雙向信用評分", "CreditFrame"),
            ("✍️ 撰寫屋賃評論", "ReviewFrame"),
        ]

        for text, frame_name in buttons:
            btn = ctk.CTkButton(
                self.user_card, 
                text=text, 
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                border_width=1,
                border_color=("gray70", "gray30"),
                hover_color=("gray80", "gray20"),
                command=lambda f=frame_name: self.controller.show_frame(f)
            )
            btn.pack(fill="x", padx=20, pady=5)

        # 4. 登出按鈕
        logout_btn = ctk.CTkButton(
            self.user_card, 
            text="登出帳號", 
            fg_color="#D35B58", 
            hover_color="#C75050",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.logout
        )
        logout_btn.pack(side="bottom", fill="x", padx=20, pady=15)

    def logout(self):
        from controllers.auth_controller import AuthController
        AuthController.logout()
        self.controller.show_frame("LoginFrame")
