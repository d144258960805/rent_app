import customtkinter as ctk
from tkinter import filedialog, messagebox
from controllers.auth_controller import Session
from controllers.verify_controller import VerifyController

class VerifyFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 暫存本機選取檔案路徑
        self.id_card_path = ""
        self.deed_path = ""

        # 頂部導覽列
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        back_btn = ctk.CTkButton(header_frame, text="← 返回首頁", width=100, command=self.go_home)
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(header_frame, text="🛡️ 房東身份實名認證系統", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(side="left", padx=20)

        # 滾動主要內容容器
        self.content_container = ctk.CTkScrollableFrame(self)
        self.content_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.render_content()

    def go_home(self):
        self.controller.show_frame("HomeFrame")

    def render_content(self):
        """根據目前登入者的角色與狀態，動態渲染介面"""
        # 清除舊內容
        for widget in self.content_container.winfo_children():
            widget.destroy()

        user = Session.get_current_user()
        if not user:
            # 尚未登入
            err_lbl = ctk.CTkLabel(
                self.content_container, 
                text="請先登入帳號以查看此頁面！", 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            err_lbl.pack(pady=40)
            return

        role = user.get("role")
        is_verified = user.get("is_verified", 0)

        if role == "admin":
            self.render_admin_panel()
        elif role == "landlord":
            self.render_landlord_panel(user["id"], is_verified)
        else:
            self.render_student_panel()

    # ================= 1. 學生端畫面 =================
    def render_student_panel(self):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        frame.pack(pady=40, padx=20, fill="both", expand=True)

        lbl = ctk.CTkLabel(
            frame,
            text="🎓 學生身分提示",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#007AFF", "#0A84FF")
        )
        lbl.pack(pady=10)

        desc = ctk.CTkLabel(
            frame,
            text="您目前是「學生租客」身分，不需要進行房東的實名與房屋權狀認證。\n\n本平台已為您嚴格把關房東身分，所有刊登房源的房東均經過人工與產權核對，請安心看房！",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        desc.pack(pady=10)

    # ================= 2. 房東端畫面 =================
    def render_landlord_panel(self, user_id, is_verified):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        if is_verified == 1:
            # 已經通過驗證
            status_box = ctk.CTkFrame(frame, fg_color=("#E2F9E9", "#112F1B"), border_width=1, border_color="#34C759")
            status_box.pack(fill="x", pady=10, ipady=15)
            
            status_lbl = ctk.CTkLabel(
                status_box, 
                text="✅ 恭喜！您已通過房東實名與產權認證！", 
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("#28A745", "#34C759")
            )
            status_lbl.pack(pady=10)
            
            info_lbl = ctk.CTkLabel(
                status_box,
                text="您的帳號已解鎖「刊登房源」權限，且享有逢甲學生的優先曝光待遇。\n感謝您與我們一同維護資訊安全透明的租屋環境！",
                font=ctk.CTkFont(size=13)
            )
            info_lbl.pack()

        elif is_verified == 2:
            # 審核中
            status_box = ctk.CTkFrame(frame, fg_color=("#FFF3CD", "#2C2205"), border_width=1, border_color="#FFC107")
            status_box.pack(fill="x", pady=10, ipady=15)
            
            status_lbl = ctk.CTkLabel(
                status_box, 
                text="⏳ 驗證文件正由後端管理員進行人工核對審核中...", 
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("#856404", "#FFC107")
            )
            status_lbl.pack(pady=10)
            
            info_lbl = ctk.CTkLabel(
                status_box,
                text="工作人員正在加緊對比您的身分證件與產權證明。\n審核結果將於 24 小時內通知您，請耐心等候！",
                font=ctk.CTkFont(size=13)
            )
            info_lbl.pack()

        else:
            # 未驗證 - 顯示上傳畫面
            lbl = ctk.CTkLabel(frame, text="請上傳您的證明文件以解鎖刊登功能", font=ctk.CTkFont(size=16, weight="bold"))
            lbl.pack(pady=(0, 20))

            form = ctk.CTkFrame(frame, corner_radius=10)
            form.pack(pady=10, padx=20, fill="x")

            # 身分證上傳欄
            id_lbl = ctk.CTkLabel(form, text="1. 上傳身分證正反面影本檔案", font=ctk.CTkFont(size=13, weight="bold"))
            id_lbl.pack(anchor="w", padx=25, pady=(15, 5))
            
            self.id_path_lbl = ctk.CTkLabel(form, text="尚未選取任何檔案...", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
            self.id_path_lbl.pack(anchor="w", padx=25)
            
            self.upload_id_btn = ctk.CTkButton(form, text="📁 瀏覽檔案 (PDF/JPG/PNG)", command=self.select_id_file, width=150)
            self.upload_id_btn.pack(anchor="w", padx=25, pady=5)

            # 產權上傳欄
            deed_lbl = ctk.CTkLabel(form, text="2. 上傳該出租房屋之產權/權狀證明影本", font=ctk.CTkFont(size=13, weight="bold"))
            deed_lbl.pack(anchor="w", padx=25, pady=(15, 5))
            
            self.deed_path_lbl = ctk.CTkLabel(form, text="尚未選取任何檔案...", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray")
            self.deed_path_lbl.pack(anchor="w", padx=25)
            
            self.upload_deed_btn = ctk.CTkButton(form, text="📁 瀏覽檔案 (PDF/JPG/PNG)", command=self.select_deed_file, width=150)
            self.upload_deed_btn.pack(anchor="w", padx=25, pady=5)

            # 送出按鈕
            submit_btn = ctk.CTkButton(
                frame, 
                text="🚀 提交驗證申請", 
                fg_color="#007AFF", 
                hover_color="#0056B3",
                height=35,
                command=lambda: self.submit_audit(user_id)
            )
            submit_btn.pack(pady=20, fill="x", padx=20)

    def select_id_file(self):
        file = filedialog.askopenfilename(filetypes=[("圖片/文件檔案", "*.jpg;*.jpeg;*.png;*.pdf")])
        if file:
            self.id_card_path = file
            filename = file.split("/")[-1]
            self.id_path_lbl.configure(text=f"已選取：{filename}", text_color=("#34C759", "#34C759"))

    def select_deed_file(self):
        file = filedialog.askopenfilename(filetypes=[("圖片/文件檔案", "*.jpg;*.jpeg;*.png;*.pdf")])
        if file:
            self.deed_path = file
            filename = file.split("/")[-1]
            self.deed_path_lbl.configure(text=f"已選取：{filename}", text_color=("#34C759", "#34C759"))

    def submit_audit(self, user_id):
        if not self.id_card_path or not self.deed_path:
            messagebox.showwarning("警告", "必須上傳身分證與權狀證明！")
            return

        success, msg = VerifyController.submit_verification(user_id, self.id_card_path, self.deed_path)
        if success:
            messagebox.showinfo("上傳成功", msg)
            self.render_content() # 重新渲染
        else:
            messagebox.showerror("上傳失敗", msg)

    # ================= 3. 管理員審核端畫面 =================
    def render_admin_panel(self):
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        frame.pack(pady=15, padx=15, fill="both", expand=True)

        admin_lbl = ctk.CTkLabel(frame, text="⚙️ 管理員後台：待審核房東驗證清單", font=ctk.CTkFont(size=16, weight="bold"))
        admin_lbl.pack(anchor="w", pady=(0, 15))

        pending_list = VerifyController.get_pending_landlords()

        if not pending_list:
            no_audit_lbl = ctk.CTkLabel(
                frame, 
                text="🎉 太棒了！目前沒有任何待審核的房東申請。", 
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color="gray"
            )
            no_audit_lbl.pack(pady=40)
            return

        for pl in pending_list:
            card = ctk.CTkFrame(frame, corner_radius=10, fg_color=("#F2F2F7", "#1C1C1E"))
            card.pack(fill="x", pady=8)
            
            # 使用雙欄排版
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=0)
            
            # 左側：房東基本聯絡資訊
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="w")
            
            name_lbl = ctk.CTkLabel(
                info_frame, 
                text=f"房東姓名：{pl['username']}", 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            name_lbl.pack(anchor="w")
            
            email_lbl = ctk.CTkLabel(
                info_frame, 
                text=f"註冊信箱：{pl['email']}  |  申請時間：{pl['created_at'][:10]}", 
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            email_lbl.pack(anchor="w", pady=3)
            
            alert_lbl = ctk.CTkLabel(
                info_frame,
                text="*(證明文件已儲存於本機 assets/uploads/ 目錄下，確保隱私安全)*",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            alert_lbl.pack(anchor="w")

            # 右側：動作按鈕
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, padx=15, pady=15, sticky="e")
            
            approve_btn = ctk.CTkButton(
                btn_frame, 
                text="核准通過", 
                fg_color="#34C759", 
                hover_color="#28A745",
                width=80,
                command=lambda lid=pl["id"]: self.approve(lid)
            )
            approve_btn.pack(pady=3)
            
            reject_btn = ctk.CTkButton(
                btn_frame, 
                text="駁回申請", 
                fg_color="#D35B58", 
                hover_color="#C75050",
                width=80,
                command=lambda lid=pl["id"]: self.reject(lid)
            )
            reject_btn.pack(pady=3)

    def approve(self, landlord_id):
        success, msg = VerifyController.approve_landlord(landlord_id)
        if success:
            messagebox.showinfo("成功", msg)
            self.render_content()
        else:
            messagebox.showerror("失敗", msg)

    def reject(self, landlord_id):
        success, msg = VerifyController.reject_landlord(landlord_id)
        if success:
            messagebox.showinfo("成功", msg)
            self.render_content()
        else:
            messagebox.showerror("失敗", msg)
