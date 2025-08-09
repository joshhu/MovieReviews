# 蒙太奇之愛 (Montage of Love) v1.0

一個專為華語影迷打造的電影評論社區，提供深入的影評分享與可信的評分參考。

## 🎯 專案特色

- **5星制評分系統**：提供精確的評分機制
- **深度評論**：最多500字的詳細影評分享
- **智慧排行榜**：每日自動更新，依評論數與上映日排序
- **進階搜尋**：支援電影標題、使用者、評論內容搜尋
- **英雄輪播**：精選熱門電影海報展示
- **管理後台**：完整的 CRUD 管理功能

## 🛠 技術架構

- **後端**：Python 3.12 + Flask + SQLAlchemy
- **資料庫**：SQLite（啟用 WAL 模式）
- **前端**：Tailwind CSS + Vanilla JavaScript
- **安全性**：bcrypt 密碼雜湊、CSRF 保護、Session 管理
- **郵件服務**：Gmail SMTP（雙重確認）
- **排程任務**：APScheduler（每日更新排行榜）
- **日誌系統**：TimedRotatingFileHandler（每日輪替，保留7天）

## 📋 系統需求

- Python 3.12+
- Gmail 應用程式密碼（用於發送郵件）
- TMDb API 金鑰（用於電影資料）

## 🚀 快速開始

### 1. 下載專案

```bash
cd montage
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 環境設定

建立 `.env` 檔案（參考 `.env.example`）：

```env
# Flask 設定
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# 資料庫
DATABASE_URL=sqlite:///app.db

# Gmail SMTP 設定
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# TMDb API
TMDB_API_KEY=your-tmdb-api-key
TMDB_BASE_URL=https://api.themoviedb.org/3

# 其他設定
LOG_LEVEL=ERROR
LOG_FILE=logs/app.log
```

### 4. 初始化資料庫

```bash
python -c "from app import create_app; from app import db; app = create_app(); app.app_context().push(); db.create_all()"
```

### 5. 啟動應用程式

```bash
python run.py
```

應用程式將在 `http://127.0.0.1:5000` 啟動。

## 📖 使用指南

### 使用者功能

1. **註冊帳戶**：使用電子郵件註冊，需要雙重確認
2. **瀏覽電影**：查看熱門、高分、最新電影
3. **評分評論**：對電影給予1-5星評分，撰寫500字內評論
4. **搜尋功能**：搜尋電影、使用者、評論內容
5. **個人檔案**：查看自己的評論歷史

### 管理員功能

訪問 `/admin` 進入管理後台：

- 使用者管理：查看、編輯使用者資料
- 電影管理：新增、編輯、刪除電影
- 評論管理：審核、編輯、刪除評論
- 統計資訊：查看系統使用統計

## 🗂 專案結構

```
montage/
├── app/
│   ├── __init__.py          # Flask 應用程式工廠
│   ├── models.py            # 資料模型
│   ├── routes.py            # 主要路由
│   ├── admin.py             # Flask-Admin 設定
│   ├── scheduler.py         # 排程任務
│   ├── email_utils.py       # 郵件功能
│   ├── auth/                # 認證模組
│   │   ├── __init__.py      # 認證路由
│   │   └── forms.py         # 表單定義
│   └── templates/           # Jinja2 模板
├── static/                  # 靜態檔案
├── migrations/              # 資料庫遷移
├── logs/                    # 日誌檔案
├── config.py               # 設定檔
├── requirements.txt        # Python 依賴
├── run.py                  # 應用程式入口
└── README.md              # 專案說明
```

## 🔧 設定說明

### Gmail 應用程式密碼設定

1. 前往 Google 帳戶設定
2. 啟用兩步驟驗證
3. 生成應用程式密碼
4. 將密碼設定到 `MAIL_PASSWORD` 環境變數

### TMDb API 設定

1. 前往 [TMDb](https://www.themoviedb.org/) 註冊帳戶
2. 申請 API 金鑰
3. 將金鑰設定到 `TMDB_API_KEY` 環境變數

## 📊 排程任務

系統會自動執行以下排程任務：

- **每日 02:00**：更新電影排行榜
- **每小時**：清理過期的確認令牌

## 🔒 安全特性

- bcrypt 密碼雜湊（含隨機鹽值）
- CSRF 攻擊防護
- Session 安全設定
- 電子郵件雙重確認
- 密碼重設連結30分鐘過期
- 參數化查詢防止 SQL 注入

## 📝 日誌管理

- 只記錄 ERROR 級別以上的日誌
- 每天午夜自動輪替日誌檔案
- 保留最近7天的日誌
- 敏感資訊不會寫入日誌

## 🚦 開發狀態

### 已完成功能

✅ 使用者註冊/登入/登出  
✅ 電子郵件雙重確認  
✅ 密碼重設功能  
✅ 電影評分與評論  
✅ 搜尋與篩選  
✅ 排行榜系統  
✅ 英雄輪播  
✅ 管理後台  
✅ 排程任務  
✅ 日誌系統  

### 未來規劃

- 檢舉系統
- 自動化測試
- MySQL 資料庫支援
- CI/CD 部署
- 推薦演算法
- 使用者行為分析

## 🤝 貢獻指南

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/新功能`)
3. 提交變更 (`git commit -am '新增某功能'`)
4. 推送到分支 (`git push origin feature/新功能`)
5. 建立 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

## 📞 聯絡資訊

如有任何問題或建議，歡迎透過以下方式聯絡：

- Email: [你的電子郵件]
- GitHub Issues: [專案議題頁面]

---

**蒙太奇之愛** - 讓每部電影都有屬於它的故事 🎬
