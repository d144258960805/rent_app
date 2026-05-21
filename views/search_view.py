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
        
        # 初始載入所有房源
        self.controller.perform_search(keyword="", tags=[])
        
    def _setup_ui(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # 標題區塊
        title_label = ctk.CTkLabel(self, text="逢甲學生專屬 - #標籤痛點篩選網", font=("Arial", 24, "bold"), text_color="#1E3A8A")
        title_label.grid(row=0, column=0, pady=(20, 5), sticky="n")
        
        subtitle_label = ctk.CTkLabel(self, text="💡 專為逢甲同學打造的精準篩選！點選下方熱門標籤，直接避開租屋痛點", font=("Arial", 12), text_color="#4B5563")
        subtitle_label.grid(row=0, column=0, pady=(50, 5), sticky="n")
        
        # 搜尋與標籤區塊
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        # 關鍵字輸入框與搜尋按鈕
        input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=5)
        
        self.keyword_entry = ctk.CTkEntry(input_frame, placeholder_text="輸入房源名稱、地址或房型 (例如：西屯區、獨立套房)...", width=500, font=("Arial", 14))
        self.keyword_entry.pack(side="left", padx=(0, 10))
        
        search_btn = ctk.CTkButton(input_frame, text="搜尋", width=90, height=32, font=("Arial", 13, "bold"), fg_color="#2563EB", hover_color="#1D4ED8", command=self.trigger_search)
        search_btn.pack(side="left")
        
        # 標籤分類區塊 (4大痛點分類，採用 2x2 格狀版面)
        self.categories_container = ctk.CTkFrame(search_frame, fg_color="#F3F4F6", corner_radius=12)
        self.categories_container.pack(fill="x", pady=10, ipady=5)
        
        self.categories_data = [
            {
                "title": "空間與採光",
                "desc": "💡 隱私、安全與曬衣便利",
                "tags": ["獨立陽台", "非頂加", "有外窗", "落地窗", "採光好"]
            },
            {
                "title": "衛浴與生活",
                "desc": "💡 不追垃圾車、不共用洗衣機",
                "tags": ["獨立洗衣機", "垃圾代收", "電梯大樓", "乾濕分離", "養寵物", "子母車"]
            },
            {
                "title": "費用與合約",
                "desc": "💡 租金補貼與台水電大省錢！",
                "tags": ["台水台電", "免仲介費", "可申請租補"]
            },
            {
                "title": "周邊與交通",
                "desc": "💡 攸關通勤上學與遲到機率",
                "tags": ["近捷運", "離校區5分內", "有小客車/機車位"]
            }
        ]
        
        self.tag_buttons = {}
        self._build_categorized_tags()
        
        # 已選標籤顯示區
        self.selected_tags_label = ctk.CTkLabel(search_frame, text="已選標籤：無", font=("Arial", 14, "bold"), text_color="#10B981")
        self.selected_tags_label.pack(anchor="w", pady=(5, 5))
        
        # 搜尋結果清單區塊 (可滾動)
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="#F9FAFB")
        self.results_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        
    def _build_categorized_tags(self):
        """建立分類標籤的 GUI 元件"""
        # 使用 Grid 佈局將 4 個分類排列為 2x2 格狀，使排版更緊湊美觀
        for idx, cat in enumerate(self.categories_data):
            row = idx // 2
            col = idx % 2
            
            # 分類卡片框
            cat_card = ctk.CTkFrame(self.categories_container, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
            cat_card.grid(row=row, column=col, padx=8, pady=6, sticky="nsew")
            self.categories_container.grid_columnconfigure(col, weight=1)
            self.categories_container.grid_rowconfigure(row, weight=1)
            
            # 分類標題與痛點說明
            title_frame = ctk.CTkFrame(cat_card, fg_color="transparent")
            title_frame.pack(fill="x", padx=10, pady=(8, 4))
            
            title_lbl = ctk.CTkLabel(title_frame, text=cat["title"], font=("Arial", 13, "bold"), text_color="#1F2937")
            title_lbl.pack(side="left")
            
            desc_lbl = ctk.CTkLabel(title_frame, text=cat["desc"], font=("Arial", 11), text_color="#4B5563")
            desc_lbl.pack(side="right", padx=(10, 0))
            
            # 標籤按鈕流 (放置按鈕)
            buttons_frame = ctk.CTkFrame(cat_card, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=10, pady=(2, 8))
            
            # 依序擺放標籤按鈕
            for tag in cat["tags"]:
                btn = ctk.CTkButton(
                    buttons_frame, 
                    text=f"#{tag}",
                    width=65,
                    height=24,
                    font=("Arial", 11),
                    command=lambda t=tag: self.toggle_tag(t),
                    fg_color="#E5E7EB",
                    text_color="#374151",
                    hover_color="#D1D5DB"
                )
                btn.pack(side="left", padx=3, pady=2)
                self.tag_buttons[tag] = btn
                
    def toggle_tag(self, tag):
        """點擊標籤時切換選取狀態，並更新 UI、觸發搜尋"""
        if tag in self.selected_tags:
            self.selected_tags.remove(tag)
            # 還原為未選取樣式
            self.tag_buttons[tag].configure(
                fg_color="#E5E7EB", 
                text_color="#374151",
                hover_color="#D1D5DB"
            )
        else:
            self.selected_tags.add(tag)
            # 設定為已選取樣式 (翡翠綠高亮)
            self.tag_buttons[tag].configure(
                fg_color="#10B981", 
                text_color="#FFFFFF",
                hover_color="#059669"
            )
            
        # 更新已選標籤 UI
        if self.selected_tags:
            selected_text = " ".join([f"#{t}" for t in self.selected_tags])
            self.selected_tags_label.configure(text=f"已選標籤：{selected_text}")
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
            no_result = ctk.CTkLabel(self.results_frame, text="找不到符合這些標籤組合的房源 😢 請嘗試減少選取的標籤！", font=("Arial", 15), text_color="#9CA3AF")
            no_result.pack(pady=40)
            return
            
        # 顯示新結果卡片
        for i, prop in enumerate(results):
            card = ctk.CTkFrame(self.results_frame, fg_color="#FFFFFF", corner_radius=12, border_width=1, border_color="#E5E7EB")
            card.grid(row=i, column=0, padx=15, pady=10, sticky="ew")
            self.results_frame.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=1)
            
            # 左側：房源基本資訊
            left_info_frame = ctk.CTkFrame(card, fg_color="transparent")
            left_info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="w")
            
            # 房源標題
            title = ctk.CTkLabel(left_info_frame, text=prop['title'], font=("Arial", 16, "bold"), text_color="#1E3A8A")
            title.pack(anchor="w")
            
            # 房源資訊 (租金特別高亮)
            info_text = f"{prop['room_type']}  |  地址: {prop['address']}"
            info = ctk.CTkLabel(left_info_frame, text=info_text, font=("Arial", 13), text_color="#4B5563")
            info.pack(anchor="w", pady=(4, 0))
            
            price_label = ctk.CTkLabel(left_info_frame, text=f"租金: NT$ {prop['price']} / 月", font=("Arial", 14, "bold"), text_color="#DC2626")
            price_label.pack(anchor="w", pady=(2, 0))
            
            # 右側：房源擁有的標籤 (以精美 Badge 效果橫向排列)
            right_tags_frame = ctk.CTkFrame(card, fg_color="transparent")
            right_tags_frame.grid(row=0, column=1, padx=15, pady=15, sticky="e")
            
            if 'tags' in prop and prop['tags']:
                # 為了避免標籤太多擠在一起，使用一個 Flow-like 的橫向排列
                for t_idx, t in enumerate(prop['tags']):
                    # 若為目前選取中的標籤，則使用亮綠色徽章，其餘使用淡藍色
                    is_active = t in self.selected_tags
                    bg_color = "#D1FAE5" if is_active else "#EFF6FF"
                    txt_color = "#065F46" if is_active else "#1E40AF"
                    
                    t_badge = ctk.CTkLabel(
                        right_tags_frame, 
                        text=f" #{t} ", 
                        font=("Arial", 11, "bold" if is_active else "normal"),
                        fg_color=bg_color,
                        text_color=txt_color,
                        corner_radius=6
                    )
                    t_badge.pack(side="left", padx=3)
