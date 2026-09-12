import sys

from backend.analysis.cohort_eda import (
    get_target_cohort_dataframe
)


def main():

    if len(sys.argv) < 2:

        print(
            "캐릭터명을 입력해주세요."
        )

        return


    character_name = sys.argv[1]


    cohort = (
        get_target_cohort_dataframe(
            character_name
        )
    )


    if (
        cohort is None
        or cohort.empty
    ):

        print(
            "Cohort 데이터를 찾을 수 없습니다."
        )

        return


    # ==============================
    # 보석 장착 여부
    # ==============================

    with_gems = cohort[
        cohort["gem_count"] > 0
    ]

    without_gems = cohort[
        cohort["gem_count"] == 0
    ]


    print()
    print(
        "=== 보석 장착 여부 - 전투력 비교 ==="
    )

    print()


    print(
        f"보석 장착 캐릭터: "
        f"{len(with_gems)}명"
    )

    print(
        f"평균 전투력: "
        f"{with_gems['combat_power'].mean():.2f}"
    )

    print(
        f"중앙값 전투력: "
        f"{with_gems['combat_power'].median():.2f}"
    )


    print()
    print(
        f"보석 미장착 캐릭터: "
        f"{len(without_gems)}명"
    )

    print(
        f"평균 전투력: "
        f"{without_gems['combat_power'].mean():.2f}"
    )

    print(
        f"중앙값 전투력: "
        f"{without_gems['combat_power'].median():.2f}"
    )


    print()
    print(
        "=== 보석 미장착 캐릭터 상세 ==="
    )

    print()


    if without_gems.empty:

        print(
            "보석 미장착 캐릭터가 없습니다."
        )

    else:

        print(
            without_gems[
                [
                    "character_name",
                    "item_level",
                    "combat_power",
                    "weapon_enhancement"
                ]
            ]
            .sort_values(
                by="combat_power"
            )
            .to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()