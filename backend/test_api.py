import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LOSTARK_API_KEY")

character_name = "박한아린"

url = f"https://developer-lostark.game.onstove.com/armories/characters/{character_name}"

headers = {
    "accept": "application/json",
    "authorization": f"bearer {API_KEY}"
}

response = requests.get(url, headers=headers)

print("상태 코드:", response.status_code)

if response.status_code == 200:
    data = response.json()

    print("API 호출 성공")

    with open(
        f"data/raw/{character_name}.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"{character_name}.json 저장 완료")

else:
    print("API 호출 실패")
    print(response.text)