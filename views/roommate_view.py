import customtkinter as ctk
from tkinter import messagebox
from controllers.auth_controller import Session
from controllers.roommate_controller import RoommateController
from controllers.access_control import AccessControl

class RoommateFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # 頂部導覽列
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        back_btn = ctk.CTkButton(header_frame, text="← 返回首頁", width=100, command=self.go_home)
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(header_frame, text="🤝 逢甲專屬 — 揪團找室友公告欄", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(side="left", padx=20)

        # 雙欄配置 (左側顯示貼文清單，右側為發布貼文表單)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        main_container.grid_columnconfigure(0, weight=2)  # 左欄 (大)：貼文清單
        main_container.grid_columnconfigure(1, weight=1)  # 右欄 (小)：發布表單
        main_container.grid_rowconfigure(0, weight=1)

        # ================= 左側：揪室友貼文列表 =================
        left_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        self.posts_count_lbl = ctk.CTkLabel(left_panel, text="目前共有 0 則徵求公告", font=ctk.CTkFont(size=13), anchor="w")
        self.posts_count_lbl.pack(fill="x", pady=(0, 5))
        
        self.scroll_posts = ctk.CTkScrollableFrame(left_panel)
        self.scroll_posts.pack(fill="both", expand=True)

        # ================= 右側：發文面板 =================
        self.right_panel = ctk.CTkFrame(main_container, width=280)
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.pack_propagate(False)
        
        form_title = ctk.CTkLabel(self.right_panel, text="📢 發布徵室友啟事", font=ctk.CTkFont(size=16, weight="bold"))
        form_title.pack(pady=15)
        
        # 1. 標題
        t_lbl = ctk.CTkLabel(self.right_panel, text="貼文簡短標題", font=ctk.CTkFont(size=12, weight="bold"))
        t_lbl.pack(anchor="w", padx=20, pady=(5, 3))
        self.title_entry = ctk.CTkEntry(self.right_panel, placeholder_text="如：徵西安街整層室友1名")
        self.title_entry.pack(fill="x", padx=20)

        # 2. 預算金額
        r_lbl = ctk.CTkLabel(self.right_panel, text="期望租金預算 / 月", font=ctk.CTkFont(size=12, weight="bold"))
        r_lbl.pack(anchor="w", padx=20, pady=(10, 3))
        self.rent_entry = ctk.CTkEntry(self.right_panel, placeholder_text="如：5000")
        self.rent_entry.pack(fill="x", padx=20)

        # 3. 詳細描述說明
        d_lbl = ctk.CTkLabel(self.right_panel, text="習慣要求與詳細描述", font=ctk.CTkFont(size=12, weight="bold"))
        d_lbl.pack(anchor="w", padx=20, pady=(10, 3))
        self.desc_box = ctk.CTkTextbox(self.right_panel, height=120, corner_radius=6)
        self.desc_box.pack(fill="x", padx=20)
        
        # 發布按鈕
        self.post_btn = ctk.CTkButton(
            self.right_panel, 
            text="🚀 確認發布貼文", 
            fg_color="#007AFF",
            hover_color="#0056B3",
            command=self.publish_post
        )
        self.post_btn.pack(fill="x", padx=20, pady=25)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.load_posts()

    def go_home(self):
        self.controller.show_frame("HomeFrame")

    def load_posts(self):
        """從資料庫加載貼文清單"""
        posts = RoommateController.get_all_posts()
        
        self.posts_count_lbl.configure(text=f"目前共有 {len(posts)} 則徵求公告")

        # 清空列表
        for widget in self.scroll_posts.winfo_children():
            widget.destroy()

        if not posts:
            no_posts_lbl = ctk.CTkLabel(
                self.scroll_posts, 
                text="🌱 目前公告欄空空如也，快來發布第一篇貼文吧！", 
                font=ctk.CTkFont(size=13, slant="italic"),
                text_color="gray"
            )
            no_posts_lbl.pack(pady=40)
            return

        current_user = Session.get_current_user()

        for post in posts:
            post_card = ctk.CTkFrame(self.scroll_posts, corner_radius=10, fg_color=("#F2F2F7", "#1C1C1E"))
            post_card.pack(fill="x", pady=8, padx=5)
            
            # 使用格線雙欄排版
            post_card.grid_columnconfigure(0, weight=1)
            post_card.grid_columnconfigure(1, weight=0)

            # 左側：文字資訊
            info_frame = ctk.CTkFrame(post_card, fg_color="transparent")
            info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="w")

            title_lbl = ctk.CTkLabel(
                info_frame, 
                text=post["title"], 
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=("#007AFF", "#0A84FF"),
                anchor="w"
            )
            title_lbl.pack(anchor="w")

            rent_str = f"${post['expected_rent']:,} 元/月" if post["expected_rent"] else "租金面議"
            meta_lbl = ctk.CTkLabel(
                info_frame, 
                text=f"預算：{rent_str}  |  發文者：{post['username']} (信箱：{post['email']} | 信用：{post['credit_score']} 分)", 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#E65C00", "#FF9500"),
                anchor="w"
            )
            meta_lbl.pack(anchor="w", pady=4)

            desc_lbl = ctk.CTkLabel(
                info_frame, 
                text=post["description"], 
                font=ctk.CTkFont(size=13),
                justify="left",
                wraplength=350,
                anchor="w"
            )
            desc_lbl.pack(anchor="w", pady=(2, 0))

            # 右側：如果是本人的貼文，顯示刪除按鈕
            if current_user and current_user["id"] == post["user_id"]:
                btn_frame = ctk.CTkFrame(post_card, fg_color="transparent")
                btn_frame.grid(row=0, column=1, padx=15, pady=15, sticky="e")
                
                del_btn = ctk.CTkButton(
                    btn_frame, 
                    text="🗑️ 刪除", 
                    fg_color="#D35B58", 
                    hover_color="#C75050",
                    width=60,
                    command=lambda pid=post["id"]: self.delete_post(pid)
                )
                del_btn.pack()

    def publish_post(self):
        """發布揪室友貼文：整合信用存取檢查 (F-07)"""
        user = Session.get_current_user()
        if not user:
            messagebox.showwarning("警告", "請先登入帳號後再發文！")
            self.controller.show_frame("LoginFrame")
            return

        # 執行 F-07 積分檢查 (積分須 >= 80 分)
        if not AccessControl.check_access(self, "發布徵室友貼文"):
            return

        title = self.title_entry.get().strip()
        rent = self.rent_entry.get().strip()
        description = self.desc_box.get("1.0", "end").strip()

        if not title or not description:
            messagebox.showwarning("警告", "標題與描述內容均不可留空！")
            return

        success, msg = RoommateController.create_post(user["id"], title, description, rent)
        if success:
            messagebox.showinfo("成功", msg)
            
            # 清空欄位並重新載入列表
            self.title_entry.delete(0, "end")
            self.rent_entry.delete(0, "end")
            self.desc_box.delete("1.0", "end")
            
            self.load_posts()
        else:
            messagebox.showerror("失敗", msg)

    def lock_ui(self, warning_message):
        """當積分低於 80 觸發 UI 鎖定 (F-07)"""
        messagebox.showerror("權限遭鎖定", warning_message)

    def delete_post(self, post_id):
        """本人刪除貼文"""
        user = Session.get_current_user()
        if not user:
            return
            
        if messagebox.askyesno("確認", "您確定要刪除這篇徵室友貼文嗎？"):
            success, msg = RoommateController.delete_post(post_id, user["id"])
            if success:
                messagebox.showinfo("成功", msg)
                self.load_posts()
            else:
                messagebox.showerror("失敗", msg)
