import customtkinter as ctk
from controllers.credit_controller import CreditController
from database.db import get_connection

class CreditView(ctk.CTkFrame):
    def __init__(self, master, user_id, **kwargs):
        super().__init__(master, **kwargs)
        self.user_id = user_id
        
        # UI 設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # 標題
        self.title_label = ctk.CTkLabel(self, text="信用積分中心", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # 分數面板區塊
        self.score_frame = ctk.CTkFrame(self)
        self.score_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.score_frame.grid_columnconfigure(0, weight=1)
        
        self.score_label = ctk.CTkLabel(self.score_frame, text="目前積分: --", font=ctk.CTkFont(size=36, weight="bold"))
        self.score_label.grid(row=0, column=0, padx=20, pady=20)
        
        self.status_label = ctk.CTkLabel(self.score_frame, text="狀態: --", font=ctk.CTkFont(size=16))
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # 測試用控制區塊 (為了方便展示增加的)
        self.test_frame = ctk.CTkFrame(self)
        self.test_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.test_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_pay = ctk.CTkButton(self.test_frame, text="測試: 準時交租 (+5)", command=lambda: self.trigger_event("rent_paid_on_time"))
        self.btn_pay.grid(row=0, column=0, padx=10, pady=10)
        
        self.btn_delay = ctk.CTkButton(self.test_frame, text="測試: 惡意違約 (-50)", command=lambda: self.trigger_event("contract_breach_malicious"), fg_color="#D32F2F", hover_color="#B71C1C")
        self.btn_delay.grid(row=0, column=1, padx=10, pady=10)

        # 歷史紀錄清單 (Scrollable Frame)
        self.history_label = ctk.CTkLabel(self, text="積分歷史紀錄", font=ctk.CTkFont(size=18, weight="bold"))
        self.history_label.grid(row=3, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.history_frame = ctk.CTkScrollableFrame(self, height=200)
        self.history_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # 初始化資料載入
        self.refresh_ui()

    def refresh_ui(self):
        """重新整理 UI 資料"""
        # 1. 更新分數
        score = CreditController.get_score(self.user_id)
        self.score_label.configure(text=f"目前積分: {score}")
        
        # 2. 更新狀態與顏色 (小於 60 顯示紅字警告)
        if score < 60:
            self.score_label.configure(text_color="#FF5252") # 紅色
            self.status_label.configure(text="狀態: 黑名單警告 (限制部分功能)", text_color="#FF5252")
        elif score < 80:
            self.score_label.configure(text_color="#FFA000") # 橘色
            self.status_label.configure(text="狀態: 積分偏低 (限制預約與刊登)", text_color="#FFA000")
        else:
            # 依賴主題的預設顏色
            self.score_label.configure(text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
            self.status_label.configure(text="狀態: 信用良好", text_color="#4CAF50") # 綠色
            
        # 3. 重新渲染歷史紀錄
        for widget in self.history_frame.winfo_children():
            widget.destroy()
            
        logs = CreditController.get_logs(self.user_id)
        if not logs:
            lbl = ctk.CTkLabel(self.history_frame, text="尚無紀錄")
            lbl.pack(pady=10)
            
        for log in logs:
            color = "#4CAF50" if log.points > 0 else "#FF5252"
            sign = "+" if log.points > 0 else ""
            log_text = f"[{log.created_at[:19]}] {log.description} ({sign}{log.points})"
            lbl = ctk.CTkLabel(self.history_frame, text=log_text, text_color=color)
            lbl.pack(anchor="w", padx=10, pady=2)

    def trigger_event(self, event_key):
        """觸發事件並更新畫面"""
        CreditController.trigger(self.user_id, event_key)
        self.refresh_ui()

# 獨立測試腳本
if __name__ == "__main__":
    import sys
    import os
    # 加入專案根目錄到 sys.path，避免 ModuleNotFoundError
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    from database.db import init_db
    
    # 1. 初始化資料庫
    init_db()
    
    # 2. 準備假資料 (測試用)
    from database.db import get_connection
    conn = get_connection()
    # 建立一個測試用的初始用戶，分數為 100
    conn.execute("INSERT OR IGNORE INTO users (id, username, role, credit_score) VALUES (1, 'Test User', 'tenant', 100)")
    conn.commit()
    conn.close()
    
    # 3. 啟動視窗
    ctk.set_appearance_mode("Dark")
    app = ctk.CTk()
    app.geometry("500x600")
    app.title("逢甲租屋網 - 信用積分系統測試")
    
    view = CreditView(app, user_id=1)
    view.pack(fill="both", expand=True)
    
    app.mainloop()
