import customtkinter as ctk
from controllers.filter_controller import FilterController
from components.property_card import PropertyCard

class FilterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # 標題欄
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        back_btn = ctk.CTkButton(header_frame, text="← 返回首頁", width=100, command=self.go_home)
        back_btn.pack(side="left")
        
        title_label = ctk.CTkLabel(header_frame, text="🔍 房源條件分類篩選", font=ctk.CTkFont(size=22, weight="bold"))
        title_label.pack(side="left", padx=20)

        # 雙欄配置容器 (左側篩選面板，右側結果列表)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        main_container.grid_columnconfigure(0, weight=1)  # 左側篩選面板 (小)
        main_container.grid_columnconfigure(1, weight=2)  # 右側結果面板 (大)
        main_container.grid_rowconfigure(0, weight=1)

        # ================= 左側：篩選設定面板 =================
        filter_panel = ctk.CTkFrame(main_container, width=250)
        filter_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=5)
        filter_panel.pack_propagate(False) # 固定寬度
        
        panel_title = ctk.CTkLabel(filter_panel, text="設定篩選條件", font=ctk.CTkFont(size=16, weight="bold"))
        panel_title.pack(pady=15)
        
        # 1. 租金上限 (Slider)
        rent_title = ctk.CTkLabel(filter_panel, text="最高月租金金額", font=ctk.CTkFont(size=13, weight="bold"))
        rent_title.pack(anchor="w", padx=20, pady=(10, 0))
        
        self.rent_val_label = ctk.CTkLabel(filter_panel, text="不限金額", font=ctk.CTkFont(size=14, weight="bold"), text_color=("#E65C00", "#FF9500"))
        self.rent_val_label.pack(anchor="w", padx=20)
        
        # 滑桿：0 到 30,000 元 (預設 30,000 為不限)
        self.rent_slider = ctk.CTkSlider(
            filter_panel, 
            from_=3000, 
            to=30000, 
            number_of_steps=54, # 500 元一個間距
            command=self.update_rent_label
        )
        self.rent_slider.set(30000)
        self.rent_slider.pack(fill="x", padx=20, pady=5)
        
        # 2. 房型選擇 (Dropdown)
        type_title = ctk.CTkLabel(filter_panel, text="房屋房型", font=ctk.CTkFont(size=13, weight="bold"))
        type_title.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.type_menu = ctk.CTkOptionMenu(
            filter_panel, 
            values=FilterController.get_room_types()
        )
        self.type_menu.set("全部")
        self.type_menu.pack(fill="x", padx=20)
        
        # 3. 可否申請租屋補貼 (Checkbox)
        self.subsidy_var = ctk.BooleanVar(value=False)
        self.subsidy_cb = ctk.CTkCheckBox(
            filter_panel, 
            text="僅顯示可申請租金補貼", 
            variable=self.subsidy_var,
            font=ctk.CTkFont(size=12)
        )
        self.subsidy_cb.pack(anchor="w", padx=20, pady=25)
        
        # 4. 按鈕區
        apply_btn = ctk.CTkButton(filter_panel, text="開始篩選", command=self.apply_filter)
        apply_btn.pack(fill="x", padx=20, pady=(0, 10))
        
        reset_btn = ctk.CTkButton(
            filter_panel, 
            text="重設條件", 
            fg_color="transparent", 
            text_color=("gray10", "gray90"),
            border_width=1,
            command=self.reset_filter
        )
        reset_btn.pack(fill="x", padx=20)

        # ================= 右側：篩選結果面板 =================
        results_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        results_panel.grid(row=0, column=1, sticky="nsew", pady=5)
        
        self.results_count_label = ctk.CTkLabel(results_panel, text="共找到 0 筆符合條件的房源", font=ctk.CTkFont(size=13), anchor="w")
        self.results_count_label.pack(fill="x", pady=(0, 5))
        
        self.scroll_results = ctk.CTkScrollableFrame(results_panel)
        self.scroll_results.pack(fill="both", expand=True)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.apply_filter() # 每次進入此頁面時自動更新列表

    def go_home(self):
        self.controller.show_frame("HomeFrame")

    def update_rent_label(self, value):
        """滑桿拉動時即時更新標籤顯示"""
        val = int(value)
        if val >= 30000:
            self.rent_val_label.configure(text="不限金額")
        else:
            self.rent_val_label.configure(text=f"${val:,} 元以下")

    def apply_filter(self):
        """執行篩選並渲染列表"""
        slider_val = int(self.rent_slider.get())
        max_rent = None if slider_val >= 30000 else slider_val
        room_type = self.type_menu.get()
        has_subsidy = self.subsidy_var.get()
        
        # 呼叫 Controller 拿取過濾後的資料
        properties = FilterController.filter_properties(max_rent, room_type, has_subsidy)
        
        # 更新符合筆數
        self.results_count_label.configure(text=f"共找到 {len(properties)} 筆符合條件的房源")
        
        # 清除原有列表
        for widget in self.scroll_results.winfo_children():
            widget.destroy()
            
        # 重新渲染卡片
        if not properties:
            no_results_lbl = ctk.CTkLabel(
                self.scroll_results, 
                text="🏠 找不到符合條件的房源，請嘗試放寬篩選標準！", 
                font=ctk.CTkFont(size=14, slant="italic"),
                text_color="gray"
            )
            no_results_lbl.pack(pady=40)
        else:
            for prop in properties:
                card = PropertyCard(self.scroll_results, prop, self.controller)
                card.pack(fill="x", padx=10, pady=8)

    def reset_filter(self):
        """重設所有篩選條件為預設"""
        self.rent_slider.set(30000)
        self.rent_val_label.configure(text="不限金額")
        self.type_menu.set("全部")
        self.subsidy_var.set(False)
        self.apply_filter()
