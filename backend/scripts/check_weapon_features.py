import sys

import pandas as pd

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


    weapon_columns = [
        "character_name",
        "item_level",
        "combat_power",
        "weapon_enhancement",
        "weapon_item_level",
        "weapon_quality"
    ]


    available_columns = [
        column
        for column in weapon_columns
        if column in cohort.columns
    ]


    weapon_data = (
        cohort[
            available_columns
        ]
        .copy()
    )


    print()
    print(
        "=== LoaP 무기 데이터 확인 ==="
    )

    print()

    print(
        weapon_data
        .to_string(
            index=False
        )
    )


    numeric_columns = [
        column
        for column in available_columns
        if column
        not in [
            "character_name"
        ]
    ]


    print()
    print(
        "=== 무기 Feature 기술 통계 ==="
    )

    print()

    print(
        weapon_data[
            numeric_columns
        ]
        .describe()
        .T
        .round(2)
        .to_string()
    )

        # ==============================
    # 무기 Feature 상관관계
    # ==============================

    correlation_columns = [
        "weapon_enhancement",
        "weapon_item_level",
        "weapon_quality"
    ]


    print()
    print(
        "=== 무기 Feature 상관관계 ==="
    )

    print()

    print(
        weapon_data[
            correlation_columns
        ]
        .corr()
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    main()