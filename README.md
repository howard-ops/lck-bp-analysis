# LCK BP 模擬與勝率估算數據倉庫

## 專案簡介
仿照專業電競戰隊分析後台，建立 LCK 職業賽 BP 數據倉庫。
整合版本、英雄、戰隊風格、選手英雄池四個維度，實現勝率估算與選手比較分析。

## 技術架構
- **資料庫**：PostgreSQL 16
- **轉換工具**：dbt 1.11（三層架構：staging → intermediate → mart）
- **視覺化**：Power BI + Streamlit + Plotly
- **自動化**：Python 排程 + Leaguepedia API

## 核心功能
- Star Schema 設計（4 個維度表 + 6 個事實表）
- SCD Type 2 實作（選手轉會歷史追蹤）
- 英雄版本權重衰減勝率模型
- Synergy / Counter 英雄配對矩陣
- 選手數據雷達圖（KDA、分均傷害、分均經濟等）
- 自動化數據 Pipeline（每日排程）

## 資料來源
- Oracle's Elixir（LCK 比賽數據)
- Leaguepedia Cargo API（自動化抓取）

## 專案結構
\```
lck_bp/
├── models/
│   ├── staging/          # 資料清洗層
│   ├── intermediate/     # 業務邏輯層（SCD Type 2）
│   └── mart/             # 最終分析層
├── dashboard.py          # Streamlit 視覺化
├── fetch_lck_data.py     # 自動化抓取腳本
└── import_data.py        # 資料匯入腳本
\```

## 如何執行
\```bash
# 安裝依賴
pip install dbt-postgres streamlit plotly psycopg2-binary pandas

# 執行 dbt pipeline
dbt run
dbt test

# 啟動視覺化儀表板
streamlit run dashboard.py
\```
