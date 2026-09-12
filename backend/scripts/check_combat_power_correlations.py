import sys

from backend.analysis.cohort_eda import (
    get_combat_power_correlations
)


def main():

    if len(sys.argv) < 2:

        print(
            "캐릭터명을 입력해주세요."
        )

        return


    character_name = sys.argv[1]


    result = (
        get_combat_power_correlations(
            character_name
        )
    )


    if (
        result is None
        or result.empty
    ):

        print(
            "분석 가능한 데이터가 없습니다."
        )

        return


    print()
    print(
        "=== Feature - 전투력 상관관계 ==="
    )

    print()

    print(
        result.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()