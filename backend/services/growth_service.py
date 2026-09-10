from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import (
    Character,
    CharacterSnapshot
)


def calculate_delta(
    current_value,
    previous_value
):
    """
    현재 값과 이전 값의 차이를 계산한다.
    """

    if (
        current_value is None
        or previous_value is None
    ):
        return None

    delta = (
        current_value
        - previous_value
    )

    if isinstance(delta, float):
        delta = round(delta, 2)

    return delta

def snapshot_to_dict(snapshot):
    """
    Snapshot 객체에서
    성장 비교에 필요한 값만 추출한다.
    """

    return {
        "captured_at": snapshot.captured_at,

        "item_level":
            snapshot.item_level,

        "combat_power":
            snapshot.combat_power,

        "attack_power":
            snapshot.attack_power,

        "max_hp":
            snapshot.max_hp,

        "crit":
            snapshot.crit,

        "specialization":
            snapshot.specialization,

        "swiftness":
            snapshot.swiftness,

        "weapon_enhancement":
            snapshot.weapon_enhancement,

        "weapon_item_level":
            snapshot.weapon_item_level,

        "weapon_quality":
            snapshot.weapon_quality
    }

def get_latest_growth(
    character_name
):
    """
    특정 캐릭터의 최근 Snapshot 2개를
    비교하여 성장량을 반환한다.
    """

    with SessionLocal() as db:

        # ==============================
        # Character 조회
        # ==============================

        character = db.scalar(
            select(Character)
            .where(
                Character.character_name
                == character_name
            )
        )

        if character is None:

            return {
                "status": "character_not_found",
                "message":
                    "저장된 캐릭터가 없습니다."
            }


        # ==============================
        # 최근 Snapshot 2개 조회
        # ==============================

        snapshots = db.scalars(
            select(CharacterSnapshot)
            .where(
                CharacterSnapshot.character_id
                == character.id
            )
            .order_by(
                CharacterSnapshot.captured_at.desc()
            )
            .limit(2)
        ).all()


        # ==============================
        # 비교 기록 부족
        # ==============================

        if len(snapshots) < 2:

            return {
                "status": "insufficient_history",

                "character_name":
                    character.character_name,

                "snapshot_count":
                    len(snapshots),

                "message":
                    "성장 비교를 위해 "
                    "최소 2개의 Snapshot이 필요합니다."
            }


        # 가장 최신
        current = snapshots[0]

        # 바로 이전
        previous = snapshots[1]


        # ==============================
        # 변화량 계산
        # ==============================

        changes = {

            "item_level":
                calculate_delta(
                    current.item_level,
                    previous.item_level
                ),

            "combat_power":
                calculate_delta(
                    current.combat_power,
                    previous.combat_power
                ),

            "attack_power":
                calculate_delta(
                    current.attack_power,
                    previous.attack_power
                ),

            "max_hp":
                calculate_delta(
                    current.max_hp,
                    previous.max_hp
                ),

            "crit":
                calculate_delta(
                    current.crit,
                    previous.crit
                ),

            "specialization":
                calculate_delta(
                    current.specialization,
                    previous.specialization
                ),

            "swiftness":
                calculate_delta(
                    current.swiftness,
                    previous.swiftness
                ),

            "weapon_enhancement":
                calculate_delta(
                    current.weapon_enhancement,
                    previous.weapon_enhancement
                ),

            "weapon_item_level":
                calculate_delta(
                    current.weapon_item_level,
                    previous.weapon_item_level
                ),

            "weapon_quality":
                calculate_delta(
                    current.weapon_quality,
                    previous.weapon_quality
                )
        }


        return {
            "status": "ok",

            "character": {
                "character_name":
                    character.character_name,

                "server_name":
                    character.server_name,

                "class_name":
                    character.class_name
            },

            "previous":
                snapshot_to_dict(
                    previous
                ),

            "current":
                snapshot_to_dict(
                    current
                ),

            "changes":
                changes
        }

def get_growth_history(
    character_name
):
    """
    특정 캐릭터의 성장 기록을
    오래된 순서부터 반환한다.

    성장 기록에서는
    날짜, 아이템 레벨, 전투력만 사용한다.
    """

    with SessionLocal() as db:

        # ==============================
        # Character 조회
        # ==============================

        character = db.scalar(
            select(Character)
            .where(
                Character.character_name
                == character_name
            )
        )

        if character is None:

            return {
                "status": "character_not_found",
                "message":
                    "저장된 캐릭터가 없습니다."
            }


        # ==============================
        # 전체 Snapshot 조회
        # ==============================

        snapshots = db.scalars(
            select(CharacterSnapshot)
            .where(
                CharacterSnapshot.character_id
                == character.id
            )
            .order_by(
                CharacterSnapshot.captured_at.asc()
            )
        ).all()


        # ==============================
        # 성장 기록 생성
        # ==============================

        history = []

        for snapshot in snapshots:

            history.append({
                "captured_at":
                    snapshot.captured_at,

                "item_level":
                    snapshot.item_level,

                "combat_power":
                    snapshot.combat_power
            })


        return {
            "status": "ok",

            "character": {
                "character_name":
                    character.character_name,

                "server_name":
                    character.server_name,

                "class_name":
                    character.class_name
            },

            "snapshot_count":
                len(history),

            "history":
                history
        }