import customtkinter as ctk
from controllers.search_controller import SearchController
from components.property_card import PropertyCard

class SearchFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_tags = set()  # 用於記錄當前被選取的標籤
        self.tag_buttons = {}      # 用於記錄標籤按鈕對象以切換樣式

        # 標題欄
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        back_btn = ctk.CTkButton(header_frame, text="← 返回首頁", width=100, command=self.go_home)
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(header_frame, text="🏷️ 關鍵字與熱門標籤搜尋", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(side="left", padx=20)

        # 搜尋輸入框與按鈕列
        search_bar = ctk.CTkFrame(self, fg_color="transparent")
        search_bar.pack(fill="x", padx=20, pady=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_bar, 
            placeholder_text="請輸入關鍵字 (如：捷境、文華路、採光、陽台...)", 
            height=35
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 綁定 Enter 鍵觸發搜尋
        self.search_entry.bind("<Return>", lambda event: self.perform_search())
        
        search_btn = ctk.CTkButton(
            search_bar, 
            text="開始搜尋", 
            width=100, 
            height=35,
            command=self.perform_search
        )
        search_btn.pack(side="left")

        # 熱門標籤列 (點擊可多選疊加)
        tags_container = ctk.CTkFrame(self)
        tags_container.pack(fill="x", padx=20, pady=(0, 15))
        
        tags_lbl = ctk.CTkLabel(tags_container, text="熱門標籤 (可複選)：", font=ctk.CTkFont(size=12, weight="bold"))
        tags_lbl.pack(side="left", padx=(15, 10), pady=10)
        
        # 使用流式排版加載標籤按鈕
        tags_list_frame = ctk.CTkFrame(tags_container, fg_color="transparent")
        tags_list_frame.pack(side="left", fill="both", expand=True, pady=5)
        
        for tag in SearchController.get_popular_tags():
            btn = ctk.CTkButton(
                tags_list_frame,
                text=f"#{tag}",
                font=ctk.CTkFont(size=11),
                width=65,
                height=22,
                fg_color=("#E5E5EA", "#2C2C2E"),
                text_color=("black", "white"),
                hover_color=("#D1D1D6", "#3A3A3C"),
                command=lambda t=tag: self.toggle_tag(t)
            )
            btn.pack(side="left", padx=5, pady=2)
            self.tag_buttons[tag] = btn

        # 結果數量顯示與結果清單
        self.results_count_label = ctk.CTkLabel(self, text="共找到 0 筆符合的房源", font=ctk.CTkFont(size=13), anchor="w")
        self.results_count_label.pack(fill="x", padx=20, pady=(0, 5))
        
        self.scroll_results = ctk.CTkScrollableFrame(self)
        self.scroll_results.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.perform_search() # 每次進入頁面自動刷新

    def go_home(self):
        self.controller.show_frame("HomeFrame")

    def toggle_tag(self, tag):
        """切換標籤選取狀態並改變外觀樣式，且即時刷新搜尋結果"""
        btn = self.tag_buttons[tag]
        if tag in self.active_tags:
            self.active_tags.remove(tag)
            # 還原為未選取狀態的灰色
            btn.configure(
                fg_color=("#E5E5EA", "#2C2C2E"),
                text_color=("black", "white"),
                hover_color=("#D1D1D6", "#3A3A3C")
            )
        else:
            self.active_tags.add(tag)
            # 設定為選取狀態的品牌藍色
            btn.configure(
                fg_color=("#007AFF", "#0A84FF"),
                text_color="white",
                hover_color=("#0056B3", "#0062D6")
            )
        # 即時執行搜尋
        self.perform_search()

    def perform_search(self):
        """執行關鍵字與標籤的疊加搜尋並渲染畫面"""
        keyword = self.search_entry.get().strip()
        
        # 呼叫 Controller 執行 SQLite LIKE 與標籤比對
        properties = SearchController.search_properties(keyword, list(self.active_tags))
        
        # 更新符合筆數
        self.results_count_label.configure(text=f"共找到 {len(properties)} 筆符合的房源")
        
        # 清除舊列表
        for widget in self.scroll_results.winfo_children():
            widget.destroy()
            
        # 渲染搜尋結果
        if not properties:
            no_results_lbl = ctk.CTkLabel(
                self.scroll_results, 
                text="🏷️ 找不到包含對應標籤或關鍵字的房源！", 
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color="gray"
            )
            no_results_lbl.pack(pady=40)
        else:
            for prop in properties:
                card = PropertyCard(self.scroll_results, prop, self.controller)
                card.pack(fill="x", padx=10, pady=8)
