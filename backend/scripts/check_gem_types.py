from collections import Counter

from sqlalchemy import select

from backend.analysis.cohort_eda import (
    get_target_cohort_dataframe
)

from backend.db.database import SessionLocal
from backend.db.models import Character

from backend.services.comparison_service import (
    get_latest_snapshot
)


def main():

    character_name = "박한아린"

    cohort = get_target_cohort_dataframe(
        character_name
    )

    if cohort is None or cohort.empty:

        print(
            "Cohort 데이터를 찾을 수 없습니다."
        )

        return


    character_names = (
        cohort["character_name"]
        .tolist()
    )


    type_counter = Counter()

    characters_without_gems = []

    characters_with_gems = 0


    with SessionLocal() as db:

        for name in character_names:

            character = db.scalar(
                select(Character)
                .where(
                    Character.character_name
                    == name
                )
            )

            if character is None:
                continue


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


            if not gems:

                characters_without_gems.append(
                    name
                )

                continue


            characters_with_gems += 1


            for gem in gems:

                gem_type = gem.get(
                    "type"
                )

                if gem_type is None:

                    gem_type = "(None)"


                type_counter[
                    gem_type
                ] += 1


    print()
    print(
        "=== Cohort 보석 데이터 확인 ==="
    )

    print()

    print(
        f"Cohort 캐릭터 수: "
        f"{len(character_names)}"
    )

    print(
        f"보석 데이터 존재: "
        f"{characters_with_gems}"
    )

    print(
        f"보석 데이터 없음: "
        f"{len(characters_without_gems)}"
    )


    print()
    print(
        "=== 실제 gem type 종류 ==="
    )

    print()

    for gem_type, count in (
        type_counter.most_common()
    ):

        print(
            f"{gem_type}: {count}"
        )


    print()
    print(
        "=== 보석 데이터가 없는 캐릭터 ==="
    )

    print()

    for name in characters_without_gems:

        print(name)


if __name__ == "__main__":
    main()