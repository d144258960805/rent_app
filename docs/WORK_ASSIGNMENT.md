# 🏠 逢甲租屋網 — 功能模組與個人工作清單

**技術棧**：Python + CustomTkinter + SQLite  
**協作方式**：GitHub 分支開發（每人一支 feature branch）  
**人數**：7 人

---

## 📐 整體架構分層（先共識再開發）

```
rent_app/
├── main.py                  ← 程式進入點（黃柏翰負責整合）
├── database/
│   └── db.py                ← 資料庫連線與初始化（全員共用）
├── models/
│   ├── user.py              ← 使用者 Model
│   ├── property.py          ← 房源 Model
│   ├── review.py            ← 評論 Model
│   ├── roommate.py          ← 揪室友 Model
│   └── credit.py            ← 信用積分 Model
├── views/                   ← 各頁面視窗（CustomTkinter Frames）
│   ├── home_view.py         ← 首頁清單
│   ├── filter_view.py       ← 篩選 UI（陳柔溱）
│   ├── search_view.py       ← 標籤搜尋（陳家儀）
│   ├── review_view.py       ← 評論上傳（侯宣羽）
│   ├── verify_view.py       ← 房東驗證（劉晏榕）
│   ├── credit_view.py       ← 信用評分（江亞倫）
│   ├── roommate_view.py     ← 揪室友（蘇楙倫）
│   └── auth_view.py         ← 登入/註冊（黃柏翰）
├── controllers/             ← 業務邏輯層
│   └── *.py                 ← 各自對應 views
└── assets/
    └── images/              ← 圖示與背景
```

---

## 🗓️ 開發順序建議（避免互相等待）

```
Week 1：基礎建設（所有人等這層完成才能接）
  └─ 黃柏翰：建 main.py + auth_view（登入頁框架）
  └─ 共同：確認 db.py 資料表 schema

Week 2：Model 層 + 各自 View 骨架
  └─ 每人各自建立自己的 view.py 骨架（空白畫面即可）

Week 3：邏輯實作 + Controller 串接

Week 4：兩兩對接 + 整合測試 + UI 美化

Week 5：Demo 準備 + Bug 修復
```

---

## 👤 個人工作清單

---

### 🟦 黃柏翰 — 系統整合 & 登入驗證 + 積分限制存取（F-07）

**GitHub Branch**：`feature/auth-and-integration`

| 步驟 | 任務 | 產出 |
|------|------|------|
| Step 1 | 建立 `main.py`：CustomTkinter App 主視窗、Frame 切換機制 `show_frame()` | `main.py` 可執行並切換頁面 |
| Step 2 | 建立 `database/db.py`：SQLite 連線、建表語法（users、properties、reviews、credits、roommates） | 資料庫初始化成功 |
| Step 3 | 建立 `views/auth_view.py`：登入 / 註冊 UI（CustomTkinter 表單） | 登入畫面可顯示 |
| Step 4 | 建立 `controllers/auth_controller.py`：密碼雜湊（hashlib）、帳號查詢、Session 管理 | 可真正登入並記住 user_id |
| Step 5 | 實作 F-07 積分限制：`controllers/access_control.py`，積分 < 80 時呼叫對應 View 的 `lock_ui()` | 積分不足時按鈕 disabled |
| Step 6 | 整合所有 view，讓 `main.py` 可以正確路由到各頁面 | App 可完整跑通 |
| Step 7 | 整合測試：用假資料測試登入 → 首頁 → 各功能頁面 | Demo 可正確展示 |

**⚠️ 對接需求**：
- 與**所有人**對接：提供 `get_current_user()` 與 `show_frame()` 介面
- 與**江亞倫**對接：提供 `check_credit_limit(user_id)` 供積分限制使用

---

### 🟩 陳柔溱 — 分類篩選（F-01）

**GitHub Branch**：`feature/filter`

| 步驟 | 任務 | 產出 |
|------|------|------|
| Step 1 | 設計篩選條件 UI（租金滑桿、房型下拉選單、是否有租補 Checkbox） | `filter_view.py` 畫面可顯示 |
| Step 2 | 確認 `properties` 資料表欄位（與黃柏翰對齊 schema） | 欄位名稱統一 |
| Step 3 | 建立 `controllers/filter_controller.py`：組合 SQL WHERE 條件，查詢符合的房源 | 可回傳房源 list |
| Step 4 | 將查詢結果渲染到 UI（用 CTkScrollableFrame 顯示房源卡片） | 篩選結果可顯示 |
| Step 5 | 加入「重設篩選」按鈕，清空條件重新查詢 | 功能完整 |
| Step 6 | 與陳家儀對接：確認篩選條件可與標籤搜尋疊加使用 | 兩功能不衝突 |

**⚠️ 對接需求**：
- **陳柔溱 ↔ 陳家儀**：篩選條件與標籤搜尋需可合併為同一 SQL 查詢，建議建立共用 `search_filter_controller.py`
- **陳柔溱 ↔ 黃柏翰**：篩選結果頁面要能呼叫 `show_frame("PropertyDetail")`

---

### 🟨 陳家儀 — 關鍵字標籤搜尋（F-02）

**GitHub Branch**：`feature/tag-search`

| 步驟 | 任務 | 產出 |
|------|------|------|
| Step 1 | 設計搜尋 UI：搜尋框 + 熱門標籤按鈕（落地窗、養寵物、乾濕分離等） | `search_view.py` 畫面可顯示 |
| Step 2 | 確認資料表 `property_tags`（property_id, tag_name）格式，與黃柏翰對齊 | 標籤表格確定 |
| Step 3 | 建立 `controllers/search_controller.py`：用 LIKE 或 JOIN 查詢含對應標籤的房源 | 可回傳房源 list |
| Step 4 | 搜尋結果以卡片清單顯示（可複用陳柔溱的卡片元件） | 結果畫面完成 |
| Step 5 | 加入多標籤疊加搜尋（同時選「採光好」+「養寵物」） | 進階搜尋完成 |
| Step 6 | 與陳柔溱對接：確認兩者查詢可合併 | 整合完成 |

**⚠️ 對接需求**：
- **陳家儀 ↔ 陳柔溱**：搜尋結果的房源卡片 UI 元件共用，建議抽出 `components/property_card.py`

---

### 🟧 侯宣羽 — 評論上傳（F-03）

**GitHub Branch**：`feature/review`

| 步驟 | 任務 | 產出 |
|------|------|------|
| Step 1 | 設計評論 UI：星級評分元件、文字輸入框、圖片上傳按鈕 | `review_view.py` 畫面可顯示 |
| Step 2 | 確認 `reviews` 資料表欄位（property_id, user_id, rating, comment, image_path, is_anonymous） | Schema 確定 |
| Step 3 | 建立 `controllers/review_controller.py`：新增評論、查詢房源所有評論 | CRUD 完成 |
| Step 4 | 實作圖片上傳：使用 `tkinter.filedialog` 選圖，存到 `assets/uploads/` 並記錄路徑 | 圖片可上傳 |
| Step 5 | 匿名機制：勾選匿名時顯示名稱改為「匿名租客」 | 匿名功能完成 |
| Step 6 | 在房源詳情頁嵌入評論區塊 | 整合完成 |

**⚠️ 對接需求**：
- **侯宣羽 ↔ 黃柏翰**：評論需要 `get_current_user()` 取得 user_id
- **侯宣羽 ↔ 江亞倫**：提交評論後觸發 `credit_controller.trigger(user_id, "review_submitted")`

---

### 🟥 劉晏榕 — 房東身分驗證（F-04）

**GitHub Branch**：`feature/landlord-verify`

| 步驟 | 任務 | 產出 |
|------|------|------|
| Step 1 | 設計驗證申請 UI：上傳身分證、房契按鈕，顯示「審核中」狀態 | `verify_view.py` 畫面可顯示 |
| Step 2 | 確認 `users` 資料表中的 `is_verified` 欄位，與黃柏翰對齊 | Schema 確定 |
| Step 3 | 建立 `controllers/verify_controller.py`：儲存上傳文件路徑、更新驗證狀態 | 文件上傳功能完成 |
| Step 4 | 建立管理員審核頁面：列出待審核申請，可按「通過」或「拒絕」 | 管理員可審核 |
| Step 5 | 驗證通過後，解鎖「刊登房源」按鈕 | 房東可刊登 |
| Step 6 | 安全處理：驗證完成後將敏感文件路徑隱藏，限管理員查看 | 安全機制完成 |

**⚠️ 對接需求**：
- **劉晏榕 ↔ 黃柏翰**：`is_verified` 更新需在 session 中反映
- **劉晏榕 ↔ 江亞倫**：驗證通過後呼叫 `credit_controller.trigger(user_id, "landlord_verified")`

---

### 🟪 江亞倫 — 雙向信用評分機制（F-05）

**GitHub Branch**：`feature/credit-system`

| 步驟 | 任務 | 產出 |
|------|------|------|
| Step 1 | 設計信用分數 UI：個人資料頁顯示總分、歷史記錄清單 | `credit_view.py` 畫面可顯示 |
| Step 2 | 確認 `credit_logs` 資料表（user_id, action_type, points, created_at, description） | Schema 確定 |
| Step 3 | 建立 `controllers/credit_controller.py`：`add_score()`、`deduct_score()`、`get_score()`、`trigger()` | 積分計算正確 |
| Step 4 | 定義各觸發事件積分規則（記錄於 `docs/CREDIT_EVENTS.md`），例如：準時繳租 +5、虛假房源 -20 | 規則文件完成 |
| Step 5 | 實作信用黑名單警示：積分 < 60 時，顯示紅色警示標籤 | 警示可顯示 |
| Step 6 | 提供統一的 `trigger(user_id, event)` 介面，供其他模組呼叫 | 介面統一完成 |

**⚠️ 對接需求**：
- **江亞倫 ↔ 黃柏翰**：積分 < 80 時通知 `access_control.py` 觸發權限限制
- **江亞倫 ↔ 侯宣羽**：評論送出後呼叫積分觸發
- **江亞倫 ↔ 劉晏榕**：房東驗證通過後呼叫積分初始化

---

### 🟫 蘇楙倫 — 揪團找室友區（F-06）

**GitHub Branch**：`feature/roommate`

| 步驟 | 任務 | 產出 |
|------|------|------|
| Step 1 | 設計揪室友 UI：貼文列表（CTkScrollableFrame）、發布表單（地點、人數、預算、信箱） | `roommate_view.py` 畫面可顯示 |
| Step 2 | 確認 `roommate_posts` 資料表（user_id, location, budget, people_count, fcu_email, content, created_at） | Schema 確定 |
| Step 3 | 建立 `controllers/roommate_controller.py`：新增貼文、查詢所有貼文、刪除自己的貼文 | CRUD 完成 |
| Step 4 | 實作逢甲信箱驗證：發文時檢查 email 是否為 `@fcu.edu.tw` 格式 | 信箱驗證完成 |
| Step 5 | 留言回覆功能（選做）：在貼文下顯示留言，僅限已驗證信箱者 | 進階功能完成 |
| Step 6 | 與黃柏翰對接：未登入者無法發文（導向登入頁） | 權限控制完成 |

**⚠️ 對接需求**：
- **蘇楙倫 ↔ 黃柏翰**：需從 session 取得 user 的 email 進行 FCU 信箱驗證
- **蘇楙倫 ↔ 江亞倫**：積分不足用戶的發文功能需被限制

---

## 🔗 兩兩對接矩陣

| 功能對接 | 誰發出呼叫 | 誰提供介面 | 介面函數名稱 |
|----------|-----------|-----------|------------|
| 登入 Session → 所有人 | 全員 | 黃柏翰 | `get_current_user()` |
| 頁面切換 → 所有人 | 全員 | 黃柏翰 | `show_frame(frame_name)` |
| 篩選 + 標籤搜尋合併 | 陳柔溱 | 陳家儀 | 共用 `property_card.py` 元件 |
| 評論送出 → 積分觸發 | 侯宣羽 | 江亞倫 | `credit_controller.trigger(user_id, "review_submitted")` |
| 驗證通過 → 積分初始化 | 劉晏榕 | 江亞倫 | `credit_controller.trigger(user_id, "landlord_verified")` |
| 積分不足 → 功能封鎖 | 江亞倫 | 黃柏翰 | `check_credit_limit(user_id)` |
| 室友發文 → 信箱驗證 | 蘇楙倫 | 黃柏翰 | `get_current_user().email` |

---

## 🌿 GitHub 分支策略

```
main
 └─ develop               ← 整合測試用（每週 merge 一次）
      ├─ feature/auth-and-integration   ← 黃柏翰（最先完成，其他人 base 這支）
      ├─ feature/filter                 ← 陳柔溱
      ├─ feature/tag-search             ← 陳家儀
      ├─ feature/review                 ← 侯宣羽
      ├─ feature/landlord-verify        ← 劉晏榕
      ├─ feature/credit-system          ← 江亞倫
      └─ feature/roommate               ← 蘇楙倫
```

**操作規範**：
1. 每次開始工作前：`git pull origin develop` 取得最新版本
2. 完成一個小功能就 commit：`git commit -m "feat(filter): 完成租金滑桿 UI"`
3. 要 merge 進 develop 前，先在自己 branch 跑一次 `main.py` 確認不會 crash
4. **黃柏翰的 branch 最優先 merge**，其他人等 `auth` 完成後再拉

---

## 📋 共用資源（全員注意）

| 資源 | 位置 | 誰負責維護 |
|------|------|-----------|
| 資料庫初始化 | `database/db.py` | 黃柏翰 |
| 共用 UI 元件 | `components/property_card.py` | 陳柔溱 + 陳家儀共同 |
| 積分事件定義表 | `docs/CREDIT_EVENTS.md` | 江亞倫 |
| 圖片上傳目錄 | `assets/uploads/` | 侯宣羽 |
| 主題色設定 | `main.py` 的 `ctk.set_appearance_mode()` | 黃柏翰 |

---

## ✅ 每週進度 Checklist

### Week 1 結束前
- [ ] 黃柏翰：`main.py` + `db.py` + `auth_view.py` 骨架完成
- [ ] 全員：確認並記錄 schema（`docs/SCHEMA.md`）

### Week 2 結束前
- [ ] 全員：各自的 `*_view.py` 空白畫面骨架完成
- [ ] 全員：各自的 `*_controller.py` 基本 CRUD 完成

### Week 3 結束前
- [ ] 兩兩對接完成（見對接矩陣）
- [ ] 積分系統與各模組串接完成

### Week 4 結束前
- [ ] 整合到 develop branch，整體可以 demo 跑通
- [ ] UI 美化與錯誤訊息優化

### Week 5（Demo 週）
- [ ] 準備假資料（房源 5 筆、用戶 3 筆）
- [ ] Demo 流程彩排
