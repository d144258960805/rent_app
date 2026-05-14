from models.property import PropertyModel

class SearchController:
    def __init__(self, view):
        self.view = view
        self.model = PropertyModel()
        
    def perform_search(self, tags):
        """
        處理 UI 傳來的標籤搜尋請求，呼叫 Model 並更新 View。
        :param tags: 標籤字串列表，例如 ['落地窗', '養寵物']
        """
        # 向資料庫查詢
        results = self.model.search_by_tags(tags)
        
        # 通知 View 更新畫面
        self.view.update_search_results(results)
        
    def get_popular_tags(self):
        """取得熱門標籤列表給 UI 顯示"""
        return self.model.get_all_popular_tags()
