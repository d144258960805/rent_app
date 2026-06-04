import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import Session
from controllers.review_controller import ReviewController

class ReviewFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.properties_map = {} # 記錄 title -> id 的對照表

        # 畫面置中的容器
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # 內容表單區塊
        form_frame = ctk.CTkFrame(self, corner_radius=12)
        form_frame.grid(row=1, column=1, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(form_frame, text="✍️ 發表屋賃評分與評論", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(pady=(20, 20), padx=30)

        # 1. 選擇房源
        prop_lbl = ctk.CTkLabel(form_frame, text="選擇您欲評論的房源", font=ctk.CTkFont(size=13, weight="bold"))
        prop_lbl.pack(anchor="w", padx=30, pady=(10, 5))
        
        self.prop_menu = ctk.CTkOptionMenu(form_frame, width=300)
        self.prop_menu.pack(padx=30, pady=(0, 15))

        # 2. 評分 (Segmented Button - 質感五星)
        rating_lbl = ctk.CTkLabel(form_frame, text="給予評分 (1~5 星)", font=ctk.CTkFont(size=13, weight="bold"))
        rating_lbl.pack(anchor="w", padx=30, pady=(5, 5))
        
        self.rating_btn = ctk.CTkSegmentedButton(
            form_frame, 
            values=["★ 1", "★ 2", "★ 3", "★ 4", "★ 5"],
            width=300
        )
        self.rating_btn.set("★ 5") # 預設給 5 星
        self.rating_btn.pack(padx=30, pady=(0, 15))

        # 3. 評論描述 (CTkTextbox)
        desc_lbl = ctk.CTkLabel(form_frame, text="寫下您的真實居住體驗 (非必填)", font=ctk.CTkFont(size=13, weight="bold"))
        desc_lbl.pack(anchor="w", padx=30, pady=(5, 5))
        
        self.comment_box = ctk.CTkTextbox(form_frame, width=300, height=100, corner_radius=6)
        self.comment_box.pack(padx=30, pady=(0, 15))

        # 4. 是否匿名發表 (Checkbox)
        self.anonymous_var = ctk.BooleanVar(value=False)
        self.anonymous_cb = ctk.CTkCheckBox(
            form_frame, 
            text="我希望匿名發表評論", 
            variable=self.anonymous_var,
            font=ctk.CTkFont(size=12)
        )
        self.anonymous_cb.pack(anchor="w", padx=30, pady=(0, 20))

        # 按鈕區
        submit_btn = ctk.CTkButton(
            form_frame, 
            text="送出評論 (可獲信用積分 +5)", 
            fg_color="#007AFF", 
            hover_color="#0056B3",
            width=300,
            command=self.submit_review
        )
        submit_btn.pack(pady=(0, 10))
        
        back_btn = ctk.CTkButton(
            form_frame, 
            text="返回上一頁", 
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            border_width=1,
            width=300,
            command=self.go_back
        )
        back_btn.pack(pady=(0, 20))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_properties()

    def load_properties(self):
        """動態載入系統中的所有房源以供選擇"""
        properties = ReviewController.get_properties_list()
        
        if not properties:
            self.prop_menu.configure(values=["目前無可用房源"])
            self.prop_menu.set("目前無可用房源")
            return

        # 建立 標題 -> ID 映射
        self.properties_map = {p["title"]: p["id"] for p in properties}
        self.prop_menu.configure(values=list(self.properties_map.keys()))
        
        # 檢查 Session 中是否已經有選定的房源，若有則直接預選！
        selected_id = Session.get_selected_property_id()
        if selected_id:
            for title, pid in self.properties_map.items():
                if pid == selected_id:
                    self.prop_menu.set(title)
                    break
        else:
            self.prop_menu.set(list(self.properties_map.keys())[0])

    def submit_review(self):
        """送出評論"""
        user = Session.get_current_user()
        if not user:
            messagebox.showwarning("警告", "請先登入帳號！")
            self.controller.show_frame("LoginFrame")
            return

        selected_title = self.prop_menu.get()
        property_id = self.properties_map.get(selected_title)
        
        if not property_id:
            messagebox.showwarning("警告", "請選擇一個有效房源。")
            return

        rating_str = self.rating_btn.get() # 例如 "★ 5"
        rating = int(rating_str.replace("★ ", ""))
        comment = self.comment_box.get("1.0", "end").strip()
        is_anonymous = self.anonymous_var.get()

        success, message = ReviewController.submit_review(
            property_id, user["id"], rating, comment, is_anonymous
        )
        
        if success:
            messagebox.showinfo("成功", message)
            # 清空輸入框並返回詳細頁
            self.comment_box.delete("1.0", "end")
            self.anonymous_var.set(False)
            self.controller.show_frame("PropertyDetailFrame")
        else:
            messagebox.showerror("失敗", message)

    def go_back(self):
        # 若之前有選定房源，返回詳細頁，否則返回首頁
        selected_id = Session.get_selected_property_id()
        if selected_id:
            self.controller.show_frame("PropertyDetailFrame")
        else:
            self.controller.show_frame("HomeFrame")
