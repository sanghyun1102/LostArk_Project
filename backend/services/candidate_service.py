import json
from pathlib import Path

from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import Character
from backend.services.comparison_service import (
    get_latest_snapshot
)
from backend.utils.item_level_utils import (
    get_item_level_band
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

DISCOVERED_FILE = (
    BASE_DIR
    / "data"
    / "seeds"
    / "discovered_characters.json"
)


def load_discovered_characters():

    if not DISCOVERED_FILE.exists():

        return []

    with open(
        DISCOVERED_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def find_candidates(
    character_name
):
    """
    발견된 캐릭터 중에서

    - 같은 클래스
    - 같은 5레벨 아이템 레벨 구간

    에 해당하는 캐릭터를 찾는다.
    """

    with SessionLocal() as db:

        # ==============================
        # 기준 캐릭터 조회
        # ==============================

        target_character = db.scalar(
            select(Character)
            .where(
                Character.character_name
                == character_name
            )
        )

        if target_character is None:

            return {
                "status":
                    "character_not_found",

                "message":
                    "DB에 저장된 캐릭터가 없습니다."
            }


        target_snapshot = (
            get_latest_snapshot(
                db,
                target_character.id
            )
        )

        if target_snapshot is None:

            return {
                "status":
                    "snapshot_not_found",

                "message":
                    "Snapshot이 없습니다."
            }


        target_level = (
            target_snapshot.item_level
        )

        level_band = (
            get_item_level_band(
                target_level
            )
        )

        if level_band is None:

            return {
                "status":
                    "item_level_not_found",

                "message":
                    "아이템 레벨이 없습니다."
            }


        # ==============================
        # 발견된 후보 로드
        # ==============================

        discovered = (
            load_discovered_characters()
        )

        candidates = []


        for character in discovered:

            candidate_name = (
                character.get(
                    "character_name"
                )
            )

            candidate_class = (
                character.get(
                    "class_name"
                )
            )

            candidate_level = (
                character.get(
                    "item_level"
                )
            )


            # 자기 자신 제외
            if (
                candidate_name
                == target_character.character_name
            ):
                continue


            # 같은 클래스만
            if (
                candidate_class
                != target_character.class_name
            ):
                continue


            if candidate_level is None:
                continue


            # 같은 5레벨 구간
            if not (
                level_band["start"]
                <= candidate_level
                < level_band["end"]
            ):
                continue


            candidates.append({
                "character_name":
                    candidate_name,

                "server_name":
                    character.get(
                        "server_name"
                    ),

                "class_name":
                    candidate_class,

                "item_level":
                    candidate_level
            })


        # 아이템 레벨 순 정렬
        candidates.sort(
            key=lambda character:
                character["item_level"]
        )


        return {
            "status": "ok",

            "target": {
                "character_name":
                    target_character.character_name,

                "class_name":
                    target_character.class_name,

                "item_level":
                    target_level
            },

            "item_level_band": {
                "start":
                    level_band["start"],

                "end":
                    level_band[
                        "display_end"
                    ]
            },

            "candidate_count":
                len(candidates),

            "candidates":
                candidates
        }