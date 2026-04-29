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

print("讀取 CSV 中...")
df = pd.read_csv(
    'C:/Users/user/lck-bp-project/lck_bp/datasets/2024_LoL_esports_match_data_from_OraclesElixir.csv',
    usecols=[
        'gameid', 'date', 'patch', 'league', 'side',
        'position', 'playername', 'teamname', 'champion',
        'result', 'gamelength',
        'kills', 'deaths', 'assists',
        'damagetochampions', 'damageshare',
        'damagetakenperminute', 'damagemitigatedperminute',
        'cspm', 'earnedgold', 'earnedgoldshare',
        'total cs'
    ],
    dtype=str
)

# 只留 LCK 賽區、排除隊伍整體統計列
print(f"原始資料：{len(df)} 筆")
df = df[df['league'] == 'LCK']
df = df[df['position'] != 'team']
print(f"LCK 選手資料：{len(df)} 筆")

# 清理數值欄位
numeric_cols = [
    'result', 'gamelength', 'kills', 'deaths', 'assists',
    'damagetochampions', 'damageshare', 'damagetakenperminute',
    'damagemitigatedperminute', 'cspm', 'earnedgold',
    'earnedgoldshare', 'total cs'
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 重新命名 total cs
df = df.rename(columns={'total cs': 'total_cs'})

df = df.dropna(subset=['gameid', 'playername', 'champion'])

# 清空舊資料
print("清空舊資料...")
cursor.execute("TRUNCATE TABLE raw_matches")

# 匯入資料
print("匯入資料中...")
records = df[[
    'gameid', 'date', 'patch', 'teamname', 'playername',
    'position', 'champion', 'result', 'gamelength', 'league', 'side',
    'kills', 'deaths', 'assists',
    'damagetochampions', 'damageshare',
    'damagetakenperminute', 'damagemitigatedperminute',
    'cspm', 'earnedgold', 'earnedgoldshare', 'total_cs'
]].values.tolist()

execute_values(
    cursor,
    """INSERT INTO raw_matches
       (gameid, date, patch, teamname, playername, position,
        champion, result, gamelength, league, side,
        kills, deaths, assists,
        damagetochampions, damageshare,
        damagetakenperminute, damagemitigatedperminute,
        cspm, earnedgold, earnedgoldshare, total_cs)
       VALUES %s
       ON CONFLICT (gameid, playername) DO NOTHING""",
    records
)

conn.commit()
cursor.close()
conn.close()
print(f"完成！匯入 {len(records)} 筆資料")