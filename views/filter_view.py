import customtkinter as ctk

class FilterFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ctk.CTkLabel(self, text="分類篩選 (Filter)", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=50)
        
        back_btn = ctk.CTkButton(self, text="返回首頁", command=lambda: self.controller.show_frame("HomeFrame"))
        back_btn.pack(pady=20)
