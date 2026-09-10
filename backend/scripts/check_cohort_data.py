from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import (
    Character,
    CharacterSnapshot
)
from backend.services.comparison_service import (
    get_build_name,
    get_latest_snapshot
)


def show_cohort_data():

    with SessionLocal() as db:

        characters = db.scalars(
            select(Character)
        ).all()

        print()
        print("=== 비교용 캐릭터 데이터 ===")
        print()

        for character in characters:

            snapshot = get_latest_snapshot(
                db,
                character.id
            )

            if snapshot is None:
                continue

            build_name = get_build_name(
                snapshot
            )

            print(
                f"{character.character_name}"
                f" | {character.class_name}"
                f" | {build_name}"
                f" | Lv.{snapshot.item_level}"
                f" | 전투력 {snapshot.combat_power}"
            )

        print()
        print(
            f"총 캐릭터 수: "
            f"{len(characters)}"
        )


if __name__ == "__main__":
    show_cohort_data()