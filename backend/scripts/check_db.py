from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import (
    Character,
    CharacterSnapshot
)


def show_characters():

    with SessionLocal() as db:

        characters = db.scalars(
            select(Character)
        ).all()

        print("\n=== 저장된 캐릭터 ===")

        if not characters:
            print("저장된 캐릭터가 없습니다.")
            return

        for character in characters:

            snapshots = db.scalars(
                select(CharacterSnapshot)
                .where(
                    CharacterSnapshot.character_id
                    == character.id
                )
                .order_by(
                    CharacterSnapshot.captured_at.desc()
                )
            ).all()

            print()
            print(
                f"캐릭터: "
                f"{character.character_name}"
            )

            print(
                f"서버: "
                f"{character.server_name}"
            )

            print(
                f"직업: "
                f"{character.class_name}"
            )

            print(
                f"Snapshot 개수: "
                f"{len(snapshots)}"
            )

            if snapshots:

                latest = snapshots[0]

                print("--- 최근 Snapshot ---")

                print(
                    f"저장 시간: "
                    f"{latest.captured_at}"
                )

                print(
                    f"아이템 레벨: "
                    f"{latest.item_level}"
                )

                print(
                    f"전투력: "
                    f"{latest.combat_power}"
                )

                print(
                    f"공격력: "
                    f"{latest.attack_power}"
                )

                print(
                    f"무기 강화: +"
                    f"{latest.weapon_enhancement}"
                )

                print(
                    f"무기 레벨: "
                    f"{latest.weapon_item_level}"
                )

                print(
                    f"무기 품질: "
                    f"{latest.weapon_quality}"
                )


if __name__ == "__main__":
    show_characters()