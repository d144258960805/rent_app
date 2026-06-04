import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import AuthController, Session

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 畫面置中的容器
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # 內容表單區塊
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=1, column=1, padx=20, pady=20)

        # 標題
        title_label = ctk.CTkLabel(form_frame, text="登入系統", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(0, 20))

        # Email 輸入框
        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="請輸入 Email", width=250)
        self.email_entry.pack(pady=(0, 15))

        # 密碼輸入框
        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="請輸入密碼", show="*", width=250)
        self.password_entry.pack(pady=(0, 20))

        # 登入按鈕
        login_btn = ctk.CTkButton(form_frame, text="登入", command=self.login, width=250)
        login_btn.pack(pady=(0, 10))

        # 切換註冊按鈕
        switch_to_reg_btn = ctk.CTkButton(
            form_frame, 
            text="還沒有帳號？點此註冊", 
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=lambda: self.controller.show_frame("RegisterFrame")
        )
        switch_to_reg_btn.pack()

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showwarning("警告", "請填寫所有欄位")
            return
            
        success, message = AuthController.login(email, password)
        if success:
            user = Session.get_current_user()
            messagebox.showinfo("成功", f"{message}\n歡迎回來，{user['username']} ({user['role']})")
            self.controller.show_frame("HomeFrame")
            # 清空輸入框
            self.email_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
        else:
            messagebox.showerror("登入失敗", message)

class RegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 畫面置中的容器
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # 內容表單區塊
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=1, column=1, padx=20, pady=20)

        # 標題
        title_label = ctk.CTkLabel(form_frame, text="註冊帳號", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(0, 20))

        # 使用者名稱
        self.username_entry = ctk.CTkEntry(form_frame, placeholder_text="請輸入使用者名稱", width=250)
        self.username_entry.pack(pady=(0, 15))

        # Email (包含逢甲信箱)
        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="請輸入 Email (逢甲信箱)", width=250)
        self.email_entry.pack(pady=(0, 15))

        # 密碼輸入框
        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="請輸入密碼", show="*", width=250)
        self.password_entry.pack(pady=(0, 15))

        # 角色選擇 (學生/房東)
        self.role_var = ctk.StringVar(value="student")
        
        radio_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        radio_frame.pack(pady=(0, 20), fill="x")
        
        student_radio = ctk.CTkRadioButton(radio_frame, text="我是學生", variable=self.role_var, value="student")
        student_radio.pack(side="left", padx=(0, 20))
        
        landlord_radio = ctk.CTkRadioButton(radio_frame, text="我是房東", variable=self.role_var, value="landlord")
        landlord_radio.pack(side="left")

        # 註冊按鈕
        register_btn = ctk.CTkButton(form_frame, text="註冊", command=self.register, width=250)
        register_btn.pack(pady=(0, 10))

        # 切換登入按鈕
        switch_to_login_btn = ctk.CTkButton(
            form_frame, 
            text="已經有帳號了？點此登入", 
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=lambda: self.controller.show_frame("LoginFrame")
        )
        switch_to_login_btn.pack()

    def register(self):
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if not username or not email or not password:
            messagebox.showwarning("警告", "請填寫所有欄位")
            return
            
        # 簡單驗證是否為逢甲信箱 (選用，目前只做字串檢查)
        if "@o365.fcu.edu.tw" not in email and "@fcu.edu.tw" not in email:
            messagebox.showwarning("警告", "請使用逢甲大學信箱註冊 (@o365.fcu.edu.tw 或 @fcu.edu.tw)")
            return
            
        success, message = AuthController.register(username, email, password, role)
        if success:
            messagebox.showinfo("成功", message + "\n請登入您的帳號。")
            self.controller.show_frame("LoginFrame")
            # 清空輸入框
            self.username_entry.delete(0, 'end')
            self.email_entry.delete(0, 'end')
            self.password_entry.delete(0, 'end')
        else:
            messagebox.showerror("註冊失敗", message)
