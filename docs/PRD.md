# PRD — 蒙太奇之愛 (Montage of Love) v1.0
*Date: 2025‑08‑06*

## 1. Product Overview
蒙太奇之愛是一個中文影評社區，讓影迷分享深入評論並在選片前快速取得可信評分與觀影建議。

## 2. Goals & Objectives
- 提供高品質 5 星制評分與 500 字內評論，聚焦中文內容深度。
- 3 個月內達成：MAU ≥ **3000**、每片平均 **5** 則評論、排行榜 CTR ≥ **25 %**。
- 每日自動更新排行榜以提升活躍度與留存。

## 3. Target Users
- 年齡 **15–60 歲**，主要透過串流平台觀影者。
- 使用場景：在「想看電影」的選片前造訪網站。
- 裝置：桌機 60 %、手機 40 %。

## 4. Scope (MVP)
| 功能 | 說明 |
|------|------|
| 註冊 / 登入 | E‑mail double‑opt‑in、Remember Me 30 天 |
| 評分 / 評論 | 5 ★ 整星制、影評上限 500 字、可後續編輯 |
| 排行榜 | 每日 02:00 依「評論數 ➜ 上映日」排序重新計算 |
| 搜尋 + 篩選 | 標題 / 暱稱 / 評論文字；側欄篩選類型 / 評分 / 年份；分頁顯示 |
| Hero 輪播 | 5 張海報；桌機自動 5 s、懸停暫停；手機手動 |
| 後台 | Flask‑Admin CRUD users / movies / reviews |

## 5. Non‑Functional Requirements
- 同時 **100** 併發不降速。
- ERROR 級別日誌（含 trace）；每天 00:00 輪替，保留 7 份。
- Session 7 天；閒置 30 分強登出。

## 6. Data Model
### users
user_id · email · password_hash · display_name · created_at  
### movies
movie_id · title · release_year · avg_rating · poster_url · genre_ids · runtime · tagline · overview · vote_average  
### reviews
review_id · user_id · movie_id · rating · comment_text · created_at · updated_at  

## 7. Integrations
- TMDb API 取得電影資料，使用TMDB來seeding資料庫，500部電影，必須有完整資料海報
- Gmail SMTP (App Password) 寄送驗證 / 重設信
- 所需要環境變數放在`.env`檔案中
- 使用TMDB API來取得電影資料，必須有完整資料海報，進行seeding資料庫，500部電影，必須有完整資料海報

## 8. UX / UI
Tailwind + Typography & Forms plugin；淺色預設、深色切換；卡片式網格，每列 4–5 張；側欄篩選；分頁；行動 Hero 不自動播放。

## 9. Security
bcrypt 雜湊；double‑opt‑in；重設連結 30 分鐘；CSRF；Secure HttpOnly cookies。

## 10. Logs & Monitoring
TimedRotatingFileHandler midnight +7；ERROR+trace。

## 11. Deployment
Windows 11 本機；`uv` + `pip install`; `flask run`; SQLite `app.db`; GitHub Flow 單 main 分支。

## 12. Schedule & Milestones
| 日期 | 里程碑 |
|------|--------|
| 08‑06 | PRD 定稿 |
| 08‑07 | 模型 + 遷移 |
| 08‑08 | Auth + Mail |
| 08‑09 | 評分 / 評論 |
| 08‑10 | 搜尋 / 篩選 |
| 08‑11 | 排行榜 + Scheduler |
| 08‑12 | UI & 測試，上線 |

## 13. Project Results
MVP 在本機可註冊登入、評分、搜尋、後台 CRUD；排行榜定時更新；日誌輪替；達成 KPI。

## 14. Future Iterations
檢舉系統 · 自動化測試 · MySQL 遷移 · CI/CD · 推薦算法 · Analytics

## 15. Project Directory Structure

```text
montage/
├── app/
│   ├── __init__.py          # create_app factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes.py            # main Blueprint
│   ├── admin.py             # Flask‑Admin config
│   ├── scheduler.py         # daily tasks
│   ├── email_utils.py       # Gmail SMTP helpers
│   ├── auth/                # authentication blueprint
│   │   ├── __init__.py
│   │   └── forms.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── movies/
│       │   ├── list.html
│       │   └── detail.html
│       ├── auth/
│       │   ├── login.html
│       │   ├── register.html
│       │   └── reset_request.html
│       └── admin/
│           └── dashboard.html
├── static/
│   ├── css/
│   │   └── tailwind.css
│   └── js/
│       └── app.js
├── migrations/
├── tests/
├── .env.example
├── config.py
├── requirements.txt
├── .gitignore
└── README.md
```
