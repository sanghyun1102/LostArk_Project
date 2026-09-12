from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import Character

from backend.services.comparison_service import (
    get_latest_snapshot
)


def main():

    with SessionLocal() as db:

        characters = db.scalars(
            select(Character)
        ).all()


        for character in characters:

            snapshot = get_latest_snapshot(
                db,
                character.id
            )

            if snapshot is None:
                continue


            processed_data = (
                snapshot.processed_data
                or {}
            )

            skill_gems = (
                processed_data.get(
                    "skill_gems"
                )
                or {}
            )

            gems = (
                skill_gems.get("gems")
                or []
            )


            for gem in gems:

                if gem.get("type") == "광휘":

                    print()
                    print(
                        "=== 광휘 보석 예시 ==="
                    )

                    print(
                        f"캐릭터: "
                        f"{character.character_name}"
                    )

                    print()

                    for key, value in gem.items():

                        print(
                            f"{key}: {value}"
                        )

                    return


    print(
        "광휘 보석을 찾지 못했습니다."
    )


if __name__ == "__main__":
    main()