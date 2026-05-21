import customtkinter as ctk
from controllers.auth_controller import Session

class PropertyCard(ctk.CTkFrame):
    def __init__(self, parent, property_data, controller, **kwargs):
        super().__init__(parent, corner_radius=12, **kwargs)
        self.property_data = property_data
        self.controller = controller
        
        # 設定卡片內邊距
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        # 建立左側文字資訊容器
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # 1. 標題
        title_label = ctk.CTkLabel(
            info_frame, 
            text=property_data["title"], 
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", anchor="w", pady=(0, 5))
        
        # 2. 租金與基本標籤列
        meta_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        meta_frame.pack(fill="x", anchor="w", pady=(0, 8))
        
        rent_label = ctk.CTkLabel(
            meta_frame, 
            text=f"${property_data['rent']:,} 元/月", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#E65C00", "#FF9500"), # 質感橘色
            anchor="w"
        )
        rent_label.pack(side="left", padx=(0, 15))
        
        # 房型與坪數標籤
        type_badge = ctk.CTkLabel(
            meta_frame,
            text=property_data["room_type"],
            font=ctk.CTkFont(size=11),
            fg_color=("#E5E5EA", "#2C2C2E"),
            corner_radius=6,
            padx=8,
            pady=2
        )
        type_badge.pack(side="left", padx=(0, 8))
        
        size_badge = ctk.CTkLabel(
            meta_frame,
            text=f"{property_data['size']} 坪",
            font=ctk.CTkFont(size=11),
            fg_color=("#E5E5EA", "#2C2C2E"),
            corner_radius=6,
            padx=8,
            pady=2
        )
        size_badge.pack(side="left", padx=(0, 8))
        
        if property_data["has_subsidy"]:
            subsidy_badge = ctk.CTkLabel(
                meta_frame,
                text="可租補",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("#007AFF", "#0A84FF"), # 質感藍色
                fg_color=("#E1F0FF", "#0A3054"),
                corner_radius=6,
                padx=8,
                pady=2
            )
            subsidy_badge.pack(side="left")

        # 3. 標籤清單區
        if property_data.get("tags"):
            tags_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            tags_frame.pack(fill="x", anchor="w")
            
            tags_list = [tag.strip() for tag in property_data["tags"].split(",") if tag.strip()]
            for tag in tags_list[:4]:  # 最多顯示 4 個標籤
                tag_label = ctk.CTkLabel(
                    tags_frame,
                    text=f"#{tag}",
                    font=ctk.CTkFont(size=11),
                    text_color=("#555555", "#AAAAAA"),
                )
                tag_label.pack(side="left", padx=(0, 10))

        # 右側動作按鈕區
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        action_frame.grid_rowconfigure(0, weight=1)
        
        detail_btn = ctk.CTkButton(
            action_frame, 
            text="查看詳情", 
            font=ctk.CTkFont(size=13, weight="bold"),
            width=90,
            command=self.show_details
        )
        detail_btn.grid(row=0, column=0, sticky="ew")

    def show_details(self):
        """點選後將房源 ID 存入 Session，並切換至房源詳細頁面"""
        Session.set_selected_property_id(self.property_data["id"])
        # 如果 Controller 內註冊了 PropertyDetailFrame，就進行切換
        self.controller.show_frame("PropertyDetailFrame")
