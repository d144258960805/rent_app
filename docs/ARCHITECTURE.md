# 系統架構設計 (Architecture)

**專案名稱**：逢甲租屋網 (Feng Chia Rental Platform)

本文件依據 PRD 所定義的功能與限制，規劃系統的技術架構與資料夾結構。

---

## 1. 技術架構說明

本專案採用經典的 **MVC (Model-View-Controller)** 設計模式，由後端渲染畫面，並使用輕量化技術堆疊以符合課堂規範：

- **Model (資料模型)**：負責與 SQLite 資料庫溝通。我們將使用 Python 內建的 `sqlite3` 模組（或封裝輕量化 CRUD 方法），負責處理如使用者、房源、評論等實體資料。
- **View (視圖)**：負責呈現使用者介面。採用 `Jinja2` 模板引擎渲染 HTML，並搭配原生 CSS / JavaScript (無前端框架) 進行畫面交互與樣式控制。
- **Controller (控制器)**：由 `Flask` 路由 (Routes) 擔綱，負責接收 HTTP 請求，呼叫對應的 Model 處理商業邏輯（如：身分驗證、積分計算），最後回傳渲染好的 View 給瀏覽器。

### 選用技術與原因
* **Python + Flask**：輕量、好上手，適合快速建構 API 與伺服器端渲染網頁。
* **SQLite**：無須額外架設資料庫伺服器，資料儲存於本地檔案，適合課堂專案且易於移植與備份。
* **原生 HTML/CSS/JS**：符合課堂規定，訓練前端基礎。

---

## 2. 專案資料夾結構

```text
rent_app/
├── app/                      # 應用程式主目錄
│   ├── models/               # 資料庫操作模型 (Model)
│   │   ├── __init__.py
│   │   ├── user.py           # 使用者與身分驗證邏輯
│   │   ├── property.py       # 房源相關邏輯
│   │   ├── review.py         # 評論相關邏輯
│   │   └── roommate.py       # 揪室友相關邏輯
│   ├── routes/               # Flask 路由控制器 (Controller)
│   │   ├── __init__.py
│   │   ├── auth.py           # 登入、註冊、身分審核路由
│   │   ├── property.py       # 房源瀏覽、刊登路由
│   │   ├── review.py         # 評論上傳路由
│   │   └── roommate.py       # 徵室友路由
│   ├── static/               # 靜態資源檔案
│   │   ├── css/              # 樣式表
│   │   ├── js/               # 客製化腳本
│   │   └── uploads/          # 使用者上傳之圖片/證明文件
│   └── templates/            # Jinja2 HTML 模板 (View)
│       ├── layout.html       # 共用母版
│       ├── index.html        # 首頁 / 房源清單
│       ├── property/         # 房源相關頁面
│       ├── auth/             # 認證與後台審核頁面
│       └── roommate/         # 徵室友頁面
├── database/                 # 資料庫建立語法與種子資料
│   └── schema.sql            # SQLite 建表語法
├── instance/                 # 運行時動態產生的資料
│   └── rent_app.db           # SQLite 實際資料庫檔案
├── docs/                     # 專案文件 (PRD, Architecture, DB_DESIGN 等)
├── app.py                    # Flask 應用程式進入點
├── requirements.txt          # Python 依賴套件清單
└── .gitignore                # Git 忽略名單
```

---

## 3. 元件關係圖

```mermaid
flowchart TD
    Browser[瀏覽器 (Client)]
    
    subgraph "Flask Backend"
        Router[Flask Routes (Controller)]
        Template[Jinja2 Templates (View)]
        Models[Python Models (Model)]
    end
    
    DB[(SQLite 資料庫)]
    
    Browser -- "HTTP Request (GET/POST)" --> Router
    Router -- "讀寫資料庫 (CRUD)" --> Models
    Models -- "SQL Queries" --> DB
    DB -- "回傳資料" --> Models
    Models -- "資料物件" --> Router
    Router -- "傳遞資料" --> Template
    Template -- "渲染 HTML" --> Router
    Router -- "HTTP Response (HTML/JSON)" --> Browser
```

---

## 4. 關鍵設計決策

1. **模組化路由 (Blueprints)**：
   為了避免所有路由都擠在 `app.py` 中，將採用 Flask Blueprint 將路由依功能拆分至 `app/routes/` 內，提高程式碼可維護性。

2. **本地文件儲存 (Local Uploads)**：
   針對 F-03 (評論圖片) 與 F-04 (身分驗證文件)，實作初期將圖片直接儲存於 `app/static/uploads/` 目錄中。身分驗證的敏感文件會在審核通過/拒絕後處理，以符合資安規範。

3. **實名積分整合機制**：
   使用者表中將增加 `score`（積分）與 `role`（身分）欄位，並透過裝飾器 (Decorator) 攔截請求，若 `score < 80` 則限制看房預約或刊登權限 (F-07)。
