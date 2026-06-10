import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 設定視窗基本屬性
        self.title("主視窗 (Main App)")
        self.geometry("800x600")

        # 設定外觀主題
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

        # 建立一個容器 Frame，用來放置並重疊所有的頁面 Frame
        self.container = ctk.CTkFrame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 儲存所有頁面 Frame 的字典
        self.frames = {}

        # 初始化畫面
        self._init_frames()

        # 預設顯示登入頁
        self.show_frame("LoginFrame")

    def _init_frames(self):
        """初始化並註冊所有的畫面 Frame"""
        from views.auth_view import LoginFrame, RegisterFrame
        from views.home_view import HomeFrame
        from views.filter_view import FilterFrame
        from views.search_view import SearchFrame
        from views.review_view import ReviewFrame
        from views.verify_view import VerifyFrame
        from views.credit_view import CreditFrame
        from views.roommate_view import RoommateFrame
        from views.property_detail_view import PropertyDetailFrame
        
        # 將所有需要註冊的 Frame 放到一個迴圈裡處理
        frames_to_register = (
            LoginFrame, RegisterFrame, HomeFrame, FilterFrame, 
            SearchFrame, ReviewFrame, VerifyFrame, CreditFrame, RoommateFrame,
            PropertyDetailFrame
        )
        
        for F in frames_to_register:
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        """將指定的 Frame 提升到最上層顯示"""
        if page_name in self.frames:
            frame = self.frames[page_name]
            frame.tkraise()
        else:
            print(f"Warning: Frame '{page_name}' not found!")

if __name__ == "__main__":
    app = App()
    app.mainloop()
