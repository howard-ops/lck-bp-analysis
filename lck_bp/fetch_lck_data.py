import requests
import time
import psycopg2
from psycopg2.extras import execute_values
import subprocess
import os
from datetime import datetime, timedelta

# ==========================================
# 設定
# ==========================================
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "lck_bp",
    "user": "lck_user",
    "password": "lck123456"
}

API_URL = "https://lol.fandom.com/api.php"
HEADERS = {"User-Agent": "LCK-BP-Project/1.0 (learning project)"}
DBT_PROJECT_DIR = r"C:\Users\user\lck-bp-project\lck_bp"

# ==========================================
# API 查詢（含重試機制）
# ==========================================
def query_leaguepedia(params, max_retries=5):
    for attempt in range(max_retries):
        try:
            time.sleep(2)
            response = requests.get(API_URL, params=params, headers=HEADERS)
            data = response.json()

            if 'error' in data and data['error']['code'] == 'ratelimited':
                wait = (attempt + 1) * 30
                print(f"Rate limit 觸發，等待 {wait} 秒後重試...")
                time.sleep(wait)
                continue

            return data.get('cargoquery', [])

        except Exception as e:
            print(f"請求失敗：{e}，重試中...")
            time.sleep(10)

    print("已達最大重試次數，跳過此次請求")
    return []

# ==========================================
# 抓取 LCK 比賽資料
# ==========================================
def fetch_lck_games(days_back=7):
    since = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    print(f"抓取 {since} 之後的 LCK 比賽...")

    params = {
        "action": "cargoquery",
        "tables": "ScoreboardPlayers=SP,ScoreboardGames=SG",
        "join_on": "SP.GameId=SG.GameId",
        "fields": "SG.GameId,SG.DateTime_UTC,SG.Patch,SP.Team,SP.Role,SP.Link,SP.Champion,SP.Win,SG.Gamelength",
        "where": f"SG.Tournament LIKE '%LCK%' AND SG.DateTime_UTC >= '{since}'",
        "limit": "500",
        "format": "json",
        "origin": "*"
    }

    return query_leaguepedia(params)

# ==========================================
# 整理資料格式
# ==========================================
def transform_records(raw_results):
    records = []
    for row in raw_results:
        r = row['title']
        try:
            records.append((
                r.get('GameId', ''),
                r.get('DateTime UTC', ''),
                r.get('Patch', ''),
                r.get('Team', ''),
                r.get('Link', ''),
                r.get('Role', ''),
                r.get('Champion', ''),
                1 if r.get('Win', '').lower() == 'yes' else 0,
                int(r.get('Gamelength', 0) or 0),
                'LCK',
                ''
            ))
        except Exception as e:
            print(f"資料轉換錯誤：{e}")
            continue
    return records

# ==========================================
# 存入資料庫
# ==========================================
def save_to_db(records):
    if not records:
        print("沒有新資料需要存入")
        return 0

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 用 ON CONFLICT 避免重複匯入
    execute_values(
        cursor,
        """
        INSERT INTO raw_matches
            (gameid, date, patch, teamname, playername,
             position, champion, result, gamelength, league, side)
        VALUES %s
        ON CONFLICT (gameid, playername) DO NOTHING
        """,
        records
    )

    count = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    print(f"新增 {count} 筆資料")
    return count

# ==========================================
# 執行 dbt
# ==========================================
def run_dbt():
    print("執行 dbt run...")
    result = subprocess.run(
        ["dbt", "run"],
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True
    )
    print(result.stdout[-500:])

    print("執行 dbt test...")
    result = subprocess.run(
        ["dbt", "test"],
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True
    )
    print(result.stdout[-500:])

# ==========================================
# 主程式
# ==========================================
if __name__ == "__main__":
    print(f"開始執行：{datetime.now()}")

    # 每次只抓「最近 2 天」的資料，避免重複
    raw = fetch_lck_games(days_back=2)
    print(f"從 Leaguepedia 取得 {len(raw)} 筆原始資料")

    records = transform_records(raw)
    count = save_to_db(records)

    if count > 0:
        print(f"新增 {count} 筆資料，執行 dbt...")
        run_dbt()
    else:
        print("無新資料，跳過 dbt run")

    print(f"完成：{datetime.now()}")