import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

from backend.character_parser import (
    parse_character,
    save_processed_character
)


# .env 파일 불러오기
load_dotenv()

API_KEY = os.getenv("LOSTARK_API_KEY")

BASE_URL = (
    "https://developer-lostark.game.onstove.com"
    "/armories/characters"
)


def collect_character(character_name):
    if not API_KEY:
        print("LOSTARK_API_KEY를 찾을 수 없습니다.")
        return None

    url = f"{BASE_URL}/{character_name}"

    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException as error:
        print(f"API 요청 실패: {error}")
        return None

    data = response.json()

    # ==============================
    # raw 데이터 저장
    # ==============================

    raw_dir = Path("data/raw")

    raw_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    raw_path = (
        raw_dir
        / f"{character_name}.json"
    )

    with open(
        raw_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )

    # ==============================
    # 데이터 파싱
    # ==============================

    parsed_character = parse_character(
        data
    )

    # ==============================
    # processed 데이터 저장
    # ==============================

    processed_path = (
        save_processed_character(
            parsed_character
        )
    )

    print(
        f"캐릭터 데이터 수집 완료: "
        f"{character_name}"
    )

    print(
        f"raw: {raw_path}"
    )

    print(
        f"processed: {processed_path}"
    )

    return parsed_character


def main():
    if len(sys.argv) < 2:
        print(
            "사용법: "
            "python backend/collect_character.py "
            "캐릭터이름"
        )
        return

    character_name = sys.argv[1]

    collect_character(
        character_name
    )


if __name__ == "__main__":
    main()

