import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# 資料庫連線設定
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="lck_bp",
    user="lck_user",
    password="lck123456"
)
cursor = conn.cursor()

# 三年的 CSV 檔案
csv_files = [
    'C:/Users/user/lck-bp-project/lck_bp/datasets/2024_LoL_esports_match_data_from_OraclesElixir.csv',
    'C:/Users/user/lck-bp-project/lck_bp/datasets/2025_LoL_esports_match_data_from_OraclesElixir.csv',
    'C:/Users/user/lck-bp-project/lck_bp/datasets/2026_LoL_esports_match_data_from_OraclesElixir.csv',
]

all_records = []

for csv_file in csv_files:
    year = csv_file.split('/')[-1][:4]
    print(f"讀取 {year} 年資料...")

    df = pd.read_csv(
        csv_file,
        usecols=[
            'gameid', 'date', 'patch', 'league', 'side',
            'position', 'playername', 'teamname', 'champion',
            'result', 'gamelength',
            'kills', 'deaths', 'assists',
            'damagetochampions', 'damageshare',
            'damagetakenperminute', 'damagemitigatedperminute',
            'cspm', 'earnedgold', 'earnedgoldshare',
            'total cs',
            'ban1', 'ban2', 'ban3', 'ban4', 'ban5'
        ],
        dtype=str
    )

    # 只留 LCK、排除隊伍統計列
    df = df[df['league'] == 'LCK']
    df = df[df['position'] != 'team']
    print(f"  {year} LCK 選手資料：{len(df)} 筆")

    # 清理數值欄位
    numeric_cols = [
        'result', 'gamelength', 'kills', 'deaths', 'assists',
        'damagetochampions', 'damageshare', 'damagetakenperminute',
        'damagemitigatedperminute', 'cspm', 'earnedgold',
        'earnedgoldshare', 'total cs'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.rename(columns={'total cs': 'total_cs'})
    df = df.dropna(subset=['gameid', 'playername', 'champion'])

    records = df[[
        'gameid', 'date', 'patch', 'teamname', 'playername',
        'position', 'champion', 'result', 'gamelength', 'league', 'side',
        'kills', 'deaths', 'assists',
        'damagetochampions', 'damageshare',
        'damagetakenperminute', 'damagemitigatedperminute',
        'cspm', 'earnedgold', 'earnedgoldshare', 'total_cs',
        'ban1', 'ban2', 'ban3', 'ban4', 'ban5'
    ]].values.tolist()

    all_records.extend(records)

print(f"\n總計：{len(all_records)} 筆資料")

# 清空舊資料
print("清空舊資料...")
cursor.execute("TRUNCATE TABLE raw_matches")

# 匯入資料
print("匯入資料中...")
execute_values(
    cursor,
    """INSERT INTO raw_matches
       (gameid, date, patch, teamname, playername, position,
        champion, result, gamelength, league, side,
        kills, deaths, assists,
        damagetochampions, damageshare,
        damagetakenperminute, damagemitigatedperminute,
        cspm, earnedgold, earnedgoldshare, total_cs,
        ban1, ban2, ban3, ban4, ban5)
       VALUES %s
       ON CONFLICT (gameid, playername) DO NOTHING""",
    all_records
)

conn.commit()
cursor.close()
conn.close()
print("完成！")