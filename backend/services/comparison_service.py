from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import (
    Character,
    CharacterSnapshot
)
from backend.utils.item_level_utils import (
    get_item_level_band
)


def get_build_name(snapshot):
    """
    Snapshot의 processed_data에서
    캐릭터의 핵심 빌드명을 가져온다.

    예:
    리퍼 → 갈증
    """

    if snapshot is None:
        return None

    processed_data = (
        snapshot.processed_data
        or {}
    )

    ark_passive = (
        processed_data.get(
            "ark_passive"
        )
        or {}
    )

    return ark_passive.get(
        "title"
    )


def get_latest_snapshot(
    db,
    character_id
):
    """
    특정 캐릭터의 가장 최근
    Snapshot을 반환한다.
    """

    return db.scalar(
        select(CharacterSnapshot)
        .where(
            CharacterSnapshot.character_id
            == character_id
        )
        .order_by(
            CharacterSnapshot.captured_at.desc()
        )
        .limit(1)
    )


def get_comparison_cohort(
    character_name
):
    """
    기준 캐릭터의 최종 비교 집단을 찾는다.

    조건:
    - 같은 클래스
    - 같은 빌드
    - 같은 5레벨 아이템 레벨 구간
    - 자기 자신 제외
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
                "status": "character_not_found",
                "message":
                    "저장된 캐릭터가 없습니다."
            }


        # ==============================
        # 기준 캐릭터 최신 Snapshot
        # ==============================

        target_snapshot = get_latest_snapshot(
            db,
            target_character.id
        )

        if target_snapshot is None:

            return {
                "status": "snapshot_not_found",
                "message":
                    "캐릭터 Snapshot이 없습니다."
            }


        target_item_level = (
            target_snapshot.item_level
        )

        target_build = get_build_name(
            target_snapshot
        )


        if target_item_level is None:

            return {
                "status": "item_level_not_found",
                "message":
                    "아이템 레벨 정보가 없습니다."
            }


        if target_build is None:

            return {
                "status": "build_not_found",
                "message":
                    "캐릭터 빌드 정보를 "
                    "확인할 수 없습니다."
            }


        # ==============================
        # 5레벨 고정 구간 계산
        # ==============================

        level_band = get_item_level_band(
            target_item_level
        )

        band_start = level_band["start"]
        band_end = level_band["end"]


        # ==============================
        # 같은 클래스 캐릭터 조회
        # ==============================

        characters = db.scalars(
            select(Character)
            .where(
                Character.class_name
                == target_character.class_name
            )
        ).all()


        comparison_characters = []


        # ==============================
        # 최종 비교 조건 확인
        # ==============================

        for character in characters:

            # 자기 자신 제외
            if (
                character.id
                == target_character.id
            ):
                continue


            latest_snapshot = (
                get_latest_snapshot(
                    db,
                    character.id
                )
            )

            if latest_snapshot is None:
                continue


            item_level = (
                latest_snapshot.item_level
            )

            if item_level is None:
                continue


            # ==============================
            # 같은 5레벨 구간 확인
            # ==============================

            if not (
                band_start
                <= item_level
                < band_end
            ):
                continue


            # ==============================
            # 같은 빌드 확인
            # ==============================

            build_name = get_build_name(
                latest_snapshot
            )

            if build_name != target_build:
                continue


            # ==============================
            # 최종 비교 대상
            # ==============================

            comparison_characters.append({
                "character_name":
                    character.character_name,

                "server_name":
                    character.server_name,

                "class_name":
                    character.class_name,

                "build_name":
                    build_name,

                "item_level":
                    latest_snapshot.item_level,

                "combat_power":
                    latest_snapshot.combat_power
            })


        # ==============================
        # 아이템 레벨 순 정렬
        # ==============================

        comparison_characters.sort(
            key=lambda character:
                character["item_level"]
        )


        return {
            "status": "ok",

            "target": {
                "character_name":
                    target_character.character_name,

                "server_name":
                    target_character.server_name,

                "class_name":
                    target_character.class_name,

                "build_name":
                    target_build,

                "item_level":
                    target_item_level,

                "combat_power":
                    target_snapshot.combat_power
            },

            "criteria": {
                "class_name":
                    target_character.class_name,

                "build_name":
                    target_build,

                "item_level_band": {
                    "start":
                        band_start,

                    "end":
                        level_band[
                            "display_end"
                        ]
                }
            },

            "comparison_count":
                len(
                    comparison_characters
                ),

            "characters":
                comparison_characters
        }