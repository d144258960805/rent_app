import customtkinter as ctk
from tkinter import messagebox
from database.db import get_db_connection
from controllers.auth_controller import Session
from controllers.access_control import AccessControl

class PropertyDetailFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 建立滾動區域以防內容超出
        self.scroll_container = ctk.CTkScrollableFrame(self)
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 標題與返回按鈕
        self.header_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        self.back_btn = ctk.CTkButton(
            self.header_frame, 
            text="← 返回", 
            width=80, 
            command=self.go_back
        )
        self.back_btn.pack(side="left", padx=(0, 15))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="房源詳情", 
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True)

        # 房源基本資料卡
        self.info_card = ctk.CTkFrame(self.scroll_container, corner_radius=12)
        self.info_card.pack(fill="x", pady=(0, 20))
        
        self.info_title = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=20, weight="bold"), anchor="w")
        self.info_title.pack(fill="x", padx=20, pady=(15, 5))
        
        self.info_meta = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=14), text_color=("#E65C00", "#FF9500"), anchor="w")
        self.info_meta.pack(fill="x", padx=20, pady=(0, 10))
        
        self.info_desc = ctk.CTkLabel(self.info_card, text="", font=ctk.CTkFont(size=13), justify="left", anchor="w")
        self.info_desc.pack(fill="x", padx=20, pady=(0, 15))

        # 地圖與聯絡人區
        self.contact_card = ctk.CTkFrame(self.scroll_container, corner_radius=12)
        self.contact_card.pack(fill="x", pady=(0, 20))
        
        self.contact_label = ctk.CTkLabel(self.contact_card, text="📍 地址與聯絡資訊", font=ctk.CTkFont(size=15, weight="bold"), anchor="w")
        self.contact_label.pack(fill="x", padx=20, pady=(15, 5))
        
        self.contact_text = ctk.CTkLabel(self.contact_card, text="", font=ctk.CTkFont(size=13), justify="left", anchor="w")
        self.contact_text.pack(fill="x", padx=20, pady=(0, 15))

        # 動作按鈕區
        self.action_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=(0, 20))
        
        self.book_btn = ctk.CTkButton(
            self.action_frame, 
            text="📅 預約看房 (信用檢查)", 
            fg_color="#34C759", 
            hover_color="#28A745",
            command=self.book_viewing
        )
        self.book_btn.pack(side="left", padx=(0, 15), expand=True, fill="x")
        
        self.write_review_btn = ctk.CTkButton(
            self.action_frame, 
            text="✍️ 撰寫評論", 
            command=self.write_review
        )
        self.write_review_btn.pack(side="left", expand=True, fill="x")

        # 評論展示區
        self.review_header = ctk.CTkLabel(
            self.scroll_container, 
            text="💬 真實學生評論", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            anchor="w"
        )
        self.review_header.pack(fill="x", pady=(0, 10))
        
        self.reviews_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.reviews_container.pack(fill="x")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_property_details()

    def go_back(self):
        self.controller.show_frame("HomeFrame")

    def load_property_details(self):
        """從資料庫動態載入選取的房源資訊與評論"""
        property_id = Session.get_selected_property_id()
        if not property_id:
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 取得房源細節與房東名字
        cursor.execute('''
            SELECT p.*, u.username as landlord_name, u.credit_score as landlord_credit 
            FROM properties p 
            JOIN users u ON p.landlord_id = u.id 
            WHERE p.id = ?
        ''', (property_id,))
        prop = cursor.fetchone()
        
        if not prop:
            conn.close()
            messagebox.showerror("錯誤", "找不到該房源資料。")
            self.go_back()
            return
            
        # 更新房源卡片內容
        self.info_title.configure(text=prop["title"])
        
        subsidy_text = "【可申請租屋補貼】" if prop["has_subsidy"] else "【不可申請租補】"
        meta_str = f"${prop['rent']:,} 元/月 | {prop['room_type']} | {prop['size']} 坪 | {subsidy_text}"
        self.info_meta.configure(text=meta_str)
        
        # 格式化描述文字以防長度超限
        desc_text = prop["description"] or "暫無詳細描述。"
        self.info_desc.configure(text=desc_text)
        
        # 地圖與聯絡人資訊 (模擬定位)
        contact_str = (
            f"地址：{prop['address']}\n"
            f"房東：{prop['landlord_name']} (信用積分：{prop['landlord_credit']} 分)\n"
            f"經緯度座標：北緯 {prop['latitude']:.4f}, 東經 {prop['longitude']:.4f}\n"
            f"*(點擊預約將直接導向房東聯繫信箱)"
        )
        self.contact_text.configure(text=contact_str)

        # 2. 清空舊評論並重新載入
        for widget in self.reviews_container.winfo_children():
            widget.destroy()

        cursor.execute('''
            SELECT r.*, u.username 
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            WHERE r.property_id = ? 
            ORDER BY r.created_at DESC
        ''', (property_id,))
        reviews = cursor.fetchall()
        conn.close()

        if not reviews:
            no_review_label = ctk.CTkLabel(
                self.reviews_container, 
                text="📝 目前此房源尚無任何評論，歡迎入住後成為首位評論者！", 
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color="gray"
            )
            no_review_label.pack(pady=15)
        else:
            for rev in reviews:
                # 建立一則評論的卡片
                rev_card = ctk.CTkFrame(self.reviews_container, corner_radius=8, fg_color=("#F2F2F7", "#1C1C1E"))
                rev_card.pack(fill="x", pady=5)
                
                # 星星數與作者列
                header_row = ctk.CTkFrame(rev_card, fg_color="transparent")
                header_row.pack(fill="x", padx=15, pady=(10, 5))
                
                stars = "★" * rev["rating"] + "☆" * (5 - rev["rating"])
                stars_label = ctk.CTkLabel(header_row, text=stars, font=ctk.CTkFont(size=14, weight="bold"), text_color="#FFCC00")
                stars_label.pack(side="left")
                
                author_name = "匿名租客" if rev["is_anonymous"] else rev["username"]
                author_label = ctk.CTkLabel(header_row, text=f" - By {author_name}", font=ctk.CTkFont(size=12, weight="bold"))
                author_label.pack(side="left")
                
                date_label = ctk.CTkLabel(header_row, text=rev["created_at"][:10], font=ctk.CTkFont(size=11), text_color="gray")
                date_label.pack(side="right")
                
                # 評論本文
                comment_label = ctk.CTkLabel(rev_card, text=rev["comment"] or "(僅給予評分，未寫下評語)", font=ctk.CTkFont(size=13), anchor="w", justify="left")
                comment_label.pack(fill="x", padx=15, pady=(0, 10))

    def book_viewing(self):
        """預約看房：實作 F-07 積分限制存取檢查"""
        user = Session.get_current_user()
        if not user:
            messagebox.showwarning("警告", "請先登入後再進行預約！")
            self.controller.show_frame("LoginFrame")
            return

        # 呼叫 AccessControl 檢查信用門檻是否 < 80 分
        # 為了能在 UI 上呈現限制效果，若不通過，AccessControl 將會呼叫 lock_ui
        if not AccessControl.check_access(self, "預約看房"):
            return

        # 若積分大於等於 80，則預約成功
        messagebox.showinfo("預約成功", "已發送看房預約申請給房東！\n房東將透過系統登錄信箱與您取得聯繫。")

    def lock_ui(self, warning_message):
        """當積分不足被 AccessControl 鎖定時被呼叫的 callback (F-07)"""
        messagebox.showerror("預約失敗", warning_message)

    def write_review(self):
        """切換至寫評論頁面"""
        self.controller.show_frame("ReviewFrame")
