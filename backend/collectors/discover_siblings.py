import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv(
    "LOSTARK_API_KEY"
)

BASE_URL = (
    "https://developer-lostark.game.onstove.com"
)

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

SEED_FILE = (
    BASE_DIR
    / "data"
    / "seeds"
    / "character_names.txt"
)

NAME_OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "seeds"
    / "discovered_character_names.txt"
)

DATA_OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "seeds"
    / "discovered_characters.json"
)


def to_float(value):
    if value is None:
        return None

    try:
        return float(
            str(value).replace(",", "")
        )

    except (ValueError, TypeError):
        return None


def load_seed_names():

    if not SEED_FILE.exists():

        print(
            f"Seed 파일이 없습니다: "
            f"{SEED_FILE}"
        )

        return []

    with open(
        SEED_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        names = [
            line.strip()
            for line in file
            if line.strip()
        ]

    return list(
        dict.fromkeys(names)
    )


def get_siblings(
    character_name
):

    url = (
        f"{BASE_URL}"
        f"/characters/"
        f"{character_name}"
        f"/siblings"
    )

    headers = {
        "accept":
            "application/json",

        "authorization":
            f"bearer {API_KEY}"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


def discover_siblings():

    if not API_KEY:

        print(
            "LOSTARK_API_KEY가 없습니다."
        )

        return


    seed_names = load_seed_names()

    if not seed_names:

        print(
            "Seed 캐릭터가 없습니다."
        )

        return


    # 이름 기준으로 중복 제거
    discovered = {}

    success_count = 0
    fail_count = 0


    print()
    print(
        f"Seed 캐릭터 "
        f"{len(seed_names)}명 탐색 시작"
    )

    print("=" * 45)


    for index, character_name in enumerate(
        seed_names,
        start=1
    ):

        print()
        print(
            f"[{index}/{len(seed_names)}] "
            f"{character_name}"
        )


        try:

            siblings = get_siblings(
                character_name
            )

            if not siblings:

                print(
                    "원정대 캐릭터 없음"
                )

                success_count += 1
                continue


            added_count = 0


            for sibling in siblings:

                sibling_name = sibling.get(
                    "CharacterName"
                )

                if not sibling_name:
                    continue


                character_info = {
                    "character_name":
                        sibling_name,

                    "server_name":
                        sibling.get(
                            "ServerName"
                        ),

                    "class_name":
                        sibling.get(
                            "CharacterClassName"
                        ),

                    "character_level":
                        sibling.get(
                            "CharacterLevel"
                        ),

                    "item_level":
                        to_float(
                            sibling.get(
                                "ItemAvgLevel"
                            )
                        )
                }


                if (
                    sibling_name
                    not in discovered
                ):

                    discovered[
                        sibling_name
                    ] = character_info

                    added_count += 1


            print(
                f"원정대 캐릭터: "
                f"{len(siblings)}명"
            )

            print(
                f"새 후보 추가: "
                f"{added_count}명"
            )

            success_count += 1


        except Exception as error:

            print(
                f"탐색 실패: "
                f"{character_name}"
            )

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

            fail_count += 1

            continue


    # ==============================
    # 이름순 정렬
    # ==============================

    characters = sorted(
        discovered.values(),
        key=lambda character:
            character["character_name"]
    )


    NAME_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # ==============================
    # 이름 목록 저장
    # ==============================

    with open(
        NAME_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        for character in characters:

            file.write(
                character[
                    "character_name"
                ]
                + "\n"
            )


    # ==============================
    # 메타데이터 JSON 저장
    # ==============================

    with open(
        DATA_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            characters,
            file,
            ensure_ascii=False,
            indent=4
        )


    print()
    print("=" * 45)

    print("탐색 완료")

    print(
        f"전체 후보: "
        f"{len(characters)}명"
    )

    print(
        f"성공: "
        f"{success_count}"
    )

    print(
        f"실패: "
        f"{fail_count}"
    )

    print()
    print(
        f"이름 목록: "
        f"{NAME_OUTPUT_FILE}"
    )

    print(
        f"후보 데이터: "
        f"{DATA_OUTPUT_FILE}"
    )


if __name__ == "__main__":
    discover_siblings()