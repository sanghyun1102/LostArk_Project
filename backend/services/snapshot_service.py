from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import (
    Character,
    CharacterSnapshot
)


def save_character_snapshot(
    character_data
):
    """
    파싱된 캐릭터 데이터를 DB에 저장한다.

    같은 캐릭터의 직전 데이터와 완전히 같으면
    새로운 Snapshot을 생성하지 않는다.
    """

    profile = character_data.get(
        "profile",
        {}
    )

    weapon = character_data.get(
        "weapon"
    ) or {}

    character_name = profile.get(
        "character_name"
    )

    if not character_name:
        print(
            "캐릭터 이름이 없어 "
            "DB 저장을 건너뜁니다."
        )
        return None


    # ==============================
    # DB Session 시작
    # ==============================

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


        # ==============================
        # Character가 없으면 생성
        # ==============================

        if character is None:

            character = Character(
                character_name=character_name,
                server_name=profile.get(
                    "server_name"
                ),
                class_name=profile.get(
                    "class_name"
                )
            )

            db.add(character)

            # INSERT를 실행하여
            # character.id를 받아온다.
            db.flush()

            print(
                f"새 캐릭터 등록: "
                f"{character_name}"
            )


        # ==============================
        # 캐릭터 기본정보 갱신
        # ==============================

        character.server_name = profile.get(
            "server_name"
        )

        character.class_name = profile.get(
            "class_name"
        )


        # ==============================
        # 가장 최근 Snapshot 조회
        # ==============================

        latest_snapshot = db.scalar(
            select(CharacterSnapshot)
            .where(
                CharacterSnapshot.character_id
                == character.id
            )
            .order_by(
                CharacterSnapshot.captured_at.desc()
            )
            .limit(1)
        )


        # ==============================
        # 이전 데이터와 동일한지 확인
        # ==============================

        if (
            latest_snapshot
            and
            latest_snapshot.processed_data
            == character_data
        ):

            db.commit()

            print(
                f"스펙 변화 없음: "
                f"{character_name}"
            )

            return latest_snapshot


        # ==============================
        # 새 Snapshot 생성
        # ==============================

        snapshot = CharacterSnapshot(

            character_id=character.id,

            item_level=profile.get(
                "item_level"
            ),

            combat_power=profile.get(
                "combat_power"
            ),

            attack_power=profile.get(
                "attack_power"
            ),

            max_hp=profile.get(
                "max_hp"
            ),

            crit=profile.get(
                "crit"
            ),

            specialization=profile.get(
                "specialization"
            ),

            swiftness=profile.get(
                "swiftness"
            ),

            weapon_enhancement=weapon.get(
                "enhancement_level"
            ),

            weapon_item_level=weapon.get(
                "item_level"
            ),

            weapon_quality=weapon.get(
                "quality"
            ),

            processed_data=character_data
        )

        db.add(snapshot)

        db.commit()

        db.refresh(snapshot)

        print(
            f"새 Snapshot 저장: "
            f"{character_name}"
        )

        return snapshot