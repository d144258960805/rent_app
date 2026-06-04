# 路由設計 (ROUTES)

## 1. 路由總覽表格

| 功能模組 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|---|---|---|---|---|
| **首頁** | GET | `/` | `index.html` | 顯示首頁、最新房源、進入各功能的入口 |
| **Auth** | GET | `/auth/register` | `auth/register.html` | 註冊頁面表單 |
| **Auth** | POST | `/auth/register` | — | 處理註冊邏輯 (區分學生/房東) |
| **Auth** | GET | `/auth/login` | `auth/login.html` | 登入頁面表單 |
| **Auth** | POST | `/auth/login` | — | 處理登入邏輯 |
| **Auth** | GET | `/auth/logout` | — | 登出並重導向至首頁 |
| **Auth** | GET | `/auth/verify` | `auth/verify.html` | 房東身分驗證上傳頁面 / 學生信箱驗證提示 |
| **Auth** | POST | `/auth/verify` | — | 處理文件上傳或發送驗證信 |
| **Property** | GET | `/properties` | `property/list.html` | 房源列表與搜尋 (依價格、房型、租補、標籤) |
| **Property** | GET | `/properties/<id>` | `property/detail.html` | 顯示單一房源詳情與歷史評論 |
| **Property** | GET | `/properties/new` | `property/new.html` | 房東刊登房源表單 |
| **Property** | POST | `/properties/new` | — | 接收表單並儲存房源至 DB |
| **Property** | POST | `/properties/<id>/delete` | — | 房東刪除自己的房源 |
| **Review** | POST | `/properties/<id>/reviews` | — | 學生新增匿名評論與評分 (附加於房源頁面) |
| **Roommate** | GET | `/roommates` | `roommate/list.html` | 揪團找室友貼文列表 |
| **Roommate** | GET | `/roommates/new` | `roommate/new.html` | 新增徵室友貼文表單 (限學生) |
| **Roommate** | POST | `/roommates/new` | — | 處理新增貼文 |

## 2. 每個路由的詳細說明

### Auth 模組 (auth_routes.py)
- `/auth/register`:
  - 輸入: `username`, `email`, `password`, `role` (student/landlord)
  - 邏輯: 檢查 email 是否重複，將密碼 hash 後存入 `users` 表。學生帳號預設未認證信箱，房東預設未驗證身分。
  - 錯誤處理: 欄位漏填或重複註冊則 flash error 並回傳表單。
- `/auth/login`:
  - 輸入: `email`, `password`
  - 邏輯: 驗證帳密，將 `user_id` 存入 session。

### Property 模組 (property_routes.py)
- `/properties`:
  - 輸入: URL 參數 `min_price`, `max_price`, `room_type`, `has_subsidy`, `tags`
  - 邏輯: 根據參數組合 SQL 查詢 `properties` 表，並回傳列表。
- `/properties/<id>`:
  - 邏輯: 查詢該房源的詳細資訊，並聯合查詢 `reviews` 表顯示過往評價。若積分低於 80 分的學生，可能限制其點擊「預約看房」按鈕。
- `/properties/new`:
  - 輸入: 標題、描述、租金等。
  - 邏輯: 檢查 user_id 是否為房東且 `is_verified` 為 true，然後新增紀錄。

### Review 模組 (review_routes.py)
- `/properties/<id>/reviews`:
  - 輸入: `rating`, `comment`, `image`
  - 邏輯: 確認登入身分為學生且未被停權，將資料存入 `reviews` 表，如果惡意評價可影響房東/房客積分。

### Roommate 模組 (roommate_routes.py)
- `/roommates/new`:
  - 邏輯: 檢查學生 `email` 是否已認證逢甲信箱，若無則禁止發文。

## 3. Jinja2 模板清單

- `base.html`: 包含 Bootstrap 5, Navbar, Flash message 區塊。
- `index.html` (首頁): 繼承 `base.html`，主視覺與搜尋入口。
- `auth/register.html`: 註冊表單。
- `auth/login.html`: 登入表單。
- `auth/verify.html`: 房東上傳身分證明表單。
- `property/list.html`: 房源清單與左側/上方篩選器。
- `property/detail.html`: 房源圖文介紹與留言區。
- `property/new.html`: 房東刊登表單。
- `roommate/list.html`: 徵室友清單。
- `roommate/new.html`: 發文表單。
