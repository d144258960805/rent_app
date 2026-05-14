import customtkinter as ctk
from controllers.search_controller import SearchController

class SearchView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # 初始化 Controller
        self.controller = SearchController(self)
        
        # 目前已選擇的標籤
        self.selected_tags = set()
        
        self._setup_ui()
        
        # 初始載入熱門標籤
        self._load_popular_tags()
        # 初始載入所有房源
        self.controller.perform_search(keyword="", tags=[])
        
    def _setup_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 標題區塊
        title_label = ctk.CTkLabel(self, text="關鍵字與標籤搜尋", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, pady=(20, 10), sticky="n")
        
        # 搜尋與標籤區塊
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # 關鍵字輸入框與搜尋按鈕
        input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=5)
        
        self.keyword_entry = ctk.CTkEntry(input_frame, placeholder_text="輸入房源名稱、地址或房型...", width=400, font=("Arial", 14))
        self.keyword_entry.pack(side="left", padx=(0, 10))
        
        search_btn = ctk.CTkButton(input_frame, text="搜尋", width=80, command=self.trigger_search)
        search_btn.pack(side="left")
        
        self.tags_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        self.tags_container.pack(fill="x", pady=15)
        
        # 已選標籤顯示區
        self.selected_tags_label = ctk.CTkLabel(search_frame, text="已選標籤：無", font=("Arial", 14))
        self.selected_tags_label.pack(anchor="w", pady=5)
        
        # 搜尋結果清單區塊 (可滾動)
        self.results_frame = ctk.CTkScrollableFrame(self)
        self.results_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        
    def _load_popular_tags(self):
        """從 Controller 取得並顯示熱門標籤"""
        popular_tags = self.controller.get_popular_tags()
        
        # 清除舊的按鈕
        for widget in self.tags_container.winfo_children():
            widget.destroy()
            
        # 建立標籤按鈕
        for tag in popular_tags:
            btn = ctk.CTkButton(
                self.tags_container, 
                text=tag,
                width=80,
                command=lambda t=tag: self.toggle_tag(t),
                fg_color="#4B5563",
                hover_color="#374151"
            )
            btn.pack(side="left", padx=5)
            
    def toggle_tag(self, tag):
        """點擊標籤時切換選取狀態，並觸發搜尋"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
        else:
            self.selected_tags.add(tag)
            
        # 更新已選標籤 UI
        if self.selected_tags:
            self.selected_tags_label.configure(text=f"已選標籤：{' '.join(self.selected_tags)}")
        else:
            self.selected_tags_label.configure(text="已選標籤：無")
            
        # 觸發 Controller 進行搜尋
        self.trigger_search()
        
    def trigger_search(self):
        """讀取關鍵字與已選標籤，並觸發搜尋"""
        keyword = self.keyword_entry.get().strip()
        self.controller.perform_search(keyword=keyword, tags=list(self.selected_tags))
        
    def update_search_results(self, results):
        """Controller 會呼叫這個方法來更新搜尋結果畫面"""
        # 清除舊結果
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        if not results:
            no_result = ctk.CTkLabel(self.results_frame, text="找不到符合條件的房源 😢", font=("Arial", 16))
            no_result.pack(pady=20)
            return
            
        # 顯示新結果卡片 (簡單實作)
        for i, prop in enumerate(results):
            card = ctk.CTkFrame(self.results_frame, fg_color="#F3F4F6", corner_radius=10)
            card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")
            card.grid_columnconfigure(1, weight=1)
            
            # 房源標題
            title = ctk.CTkLabel(card, text=prop['title'], font=("Arial", 16, "bold"), text_color="#111827")
            title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
            
            # 房源資訊
            info = ctk.CTkLabel(card, text=f"{prop['room_type']} | 租金: {prop['price']}元 | 地址: {prop['address']}", text_color="#4B5563")
            info.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="w")
            
            # 房源擁有的標籤 (如果有查出 tags)
            if 'tags' in prop and prop['tags']:
                tags_text = " ".join([f"#{t}" for t in prop['tags']])
                tags_label = ctk.CTkLabel(card, text=tags_text, font=("Arial", 12), text_color="#2563EB")
                tags_label.grid(row=0, column=1, rowspan=2, padx=10, sticky="e")
