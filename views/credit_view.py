import customtkinter as ctk
from controllers.auth_controller import Session
from controllers.credit_controller import CreditController

class CreditFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 頂部導覽列
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        back_btn = ctk.CTkButton(header_frame, text="← 返回首頁", width=100, command=self.go_home)
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(header_frame, text="⚖️ 雙向信用誠信積分機制", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(side="left", padx=20)

        # 主要內容區域
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.render_dashboard()

    def go_home(self):
        self.controller.show_frame("HomeFrame")

    def render_dashboard(self):
        """動態加載並顯示信用狀態與異動紀錄"""
        # 清除舊內容
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        user = Session.get_current_user()
        if not user:
            err_lbl = ctk.CTkLabel(
                self.content_frame, 
                text="請先登入帳號以查看此頁面！", 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            err_lbl.pack(pady=40)
            return

        # 1. 頂部儀表板
        score = user.get("credit_score", 100)
        
        # 決定顏色與文字等級說明
        if score >= 90:
            level_text = "🌟 信譽優良 (Excellent)"
            level_color = ("#28A745", "#34C759") # 綠色
            desc_text = "您的信譽極佳！享有完整看房、發文與預約特權，並享有高曝光推薦。"
        elif score >= 80:
            level_text = "👍 信用良好 (Good)"
            level_color = ("#007AFF", "#0A84FF") # 藍色
            desc_text = "您的信譽健全。繼續保持優良履約習慣，為社區建立互信基礎！"
        elif score >= 60:
            level_text = "⚠️ 警示：權限已受限 (Restricted)"
            level_color = ("#D97706", "#FF9500") # 質感橘色
            desc_text = "【警告】您的積分已低於 80 分！系統已自動限制您的預約看房與發文功能。"
        else:
            level_text = "🚫 誠信黑名單 (Blacklisted)"
            level_color = ("#D35B58", "#FF453A") # 紅色
            desc_text = "【嚴重警告】您的積分低於 60 分！您的帳號已被列入重點查核黑名單，權限全鎖定。"

        dashboard = ctk.CTkFrame(self.content_frame, corner_radius=12)
        dashboard.pack(fill="x", pady=(0, 20), ipady=10)

        # 使用左右排版
        dashboard.grid_columnconfigure(0, weight=1)
        dashboard.grid_columnconfigure(1, weight=1)
        
        # 左側大分數
        score_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        score_frame.grid(row=0, column=0, padx=20, pady=15, sticky="nsew")
        
        lbl_sub = ctk.CTkLabel(score_frame, text="您目前的信用積分", font=ctk.CTkFont(size=13), text_color="gray")
        lbl_sub.pack(anchor="w")
        
        lbl_score = ctk.CTkLabel(score_frame, text=f"{score} 分", font=ctk.CTkFont(size=44, weight="bold"), text_color=level_color)
        lbl_score.pack(anchor="w", pady=5)
        
        lbl_lvl = ctk.CTkLabel(score_frame, text=level_text, font=ctk.CTkFont(size=14, weight="bold"), text_color=level_color)
        lbl_lvl.pack(anchor="w")

        # 右側說明文字
        desc_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        desc_frame.grid(row=0, column=1, padx=20, pady=15, sticky="nsew")
        
        lbl_desc_title = ctk.CTkLabel(desc_frame, text="信用評估狀況", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_desc_title.pack(anchor="w")
        
        lbl_desc_content = ctk.CTkLabel(desc_frame, text=desc_text, font=ctk.CTkFont(size=12), justify="left", wraplength=250, anchor="w")
        lbl_desc_content.pack(anchor="w", pady=8)

        # 2. 下半部歷史變動日誌
        log_title = ctk.CTkLabel(self.content_frame, text="📋 信用積分異動歷史紀錄", font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        log_title.pack(fill="x", pady=(0, 10))

        logs_scroll = ctk.CTkScrollableFrame(self.content_frame)
        logs_scroll.pack(fill="both", expand=True)

        history = CreditController.get_score_history(user["id"])

        if not history:
            no_logs_lbl = ctk.CTkLabel(
                logs_scroll, 
                text="🌱 尚無任何積分變動紀錄。繼續保持優良租屋習慣！", 
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color="gray"
            )
            no_logs_lbl.pack(pady=40)
            return

        for record in history:
            log_card = ctk.CTkFrame(logs_scroll, corner_radius=8, fg_color=("#F2F2F7", "#1C1C1E"))
            log_card.pack(fill="x", pady=5, padx=10)
            
            # 使用格線排版
            log_card.grid_columnconfigure(0, weight=1)
            log_card.grid_columnconfigure(1, weight=0)
            
            # 左側資訊
            info_sub_frame = ctk.CTkFrame(log_card, fg_color="transparent")
            info_sub_frame.grid(row=0, column=0, padx=15, pady=10, sticky="w")
            
            reason_lbl = ctk.CTkLabel(info_sub_frame, text=record["reason"], font=ctk.CTkFont(size=13, weight="bold"))
            reason_lbl.pack(anchor="w")
            
            reviewer_lbl = ctk.CTkLabel(
                info_sub_frame, 
                text=f"核定者：{record['reviewer_name']}  |  日期：{record['created_at']}", 
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            reviewer_lbl.pack(anchor="w", pady=3)

            # 右側變動分數
            score_change = record["score_change"]
            if score_change >= 0:
                change_str = f"+{score_change}"
                change_color = ("#28A745", "#34C759") # 綠色
            else:
                change_str = f"{score_change}"
                change_color = ("#D35B58", "#FF453A") # 紅色
                
            change_lbl = ctk.CTkLabel(
                log_card, 
                text=change_str, 
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=change_color
            )
            change_lbl.grid(row=0, column=1, padx=20, pady=10, sticky="e")
