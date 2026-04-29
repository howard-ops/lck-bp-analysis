import requests
import time

time.sleep(2)

url = "https://lol.fandom.com/api.php"

params = {
    "action": "cargoquery",
    "tables": "ScoreboardGames",
    "fields": "GameId,Tournament",
    "limit": "5",
    "format": "json",
    "origin": "*"
}

headers = {
    "User-Agent": "LCK-BP-Project/1.0 (learning project)"
}

response = requests.get(url, params=params, headers=headers)
print(f"HTTP 狀態碼: {response.status_code}")
print(response.json())