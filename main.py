import os
import customtkinter as ctk
from database.db import init_db, insert_dummy_data
from views.search_view import SearchView

# 確保資料庫與測試資料已就緒
if not os.path.exists("rent_app.db"):
    print("初始化資料庫與測試資料...")
    init_db()
    insert_dummy_data()

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("逢甲租屋網 - 開發測試 (F-02 關鍵字搜尋)")
        self.geometry("900x600")
        
        # 設定整體主題
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # 載入 SearchView
        self.search_view = SearchView(self)
        self.search_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
