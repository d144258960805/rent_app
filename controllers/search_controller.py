from database.db import get_db_connection

class SearchController:
    @staticmethod
    def get_popular_tags():
        """熱門搜尋標籤"""
        return ["落地窗", "養寵物", "乾濕分離", "採光好", "近商圈", "陽台", "可開伙", "電梯大樓", "近校區"]

    @staticmethod
    def search_properties(keyword="", active_tags=None):
        """
        支援關鍵字搜尋 (模糊比對) 與多個標籤疊加篩選
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        # 1. 處理關鍵字搜尋 (比對標題、描述、地址)
        if keyword:
            kw = f"%{keyword}%"
            query += " AND (title LIKE ? OR description LIKE ? OR address LIKE ?)"
            params.extend([kw, kw, kw])
            
        # 2. 處理多標籤疊加 (所有的標籤都必須包含在 tags 欄位中)
        if active_tags:
            for tag in active_tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
                
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
from models.property import PropertyModel

class SearchController:
    def __init__(self, view):
        self.view = view
        self.model = PropertyModel()
        
    def perform_search(self, keyword="", tags=None):
        """
        處理 UI 傳來的關鍵字與標籤搜尋請求，呼叫 Model 並更新 View。
        :param keyword: 搜尋字串
        :param tags: 標籤字串列表，例如 ['落地窗', '養寵物']
        """
        tags = tags or []
        # 向資料庫查詢
        results = self.model.search(keyword=keyword, tags=tags)
        
        # 通知 View 更新畫面
        self.view.update_search_results(results)
        
    def get_popular_tags(self):
        """取得熱門標籤列表給 UI 顯示"""
        return self.model.get_all_popular_tags()
