import sys

from backend.analysis.cohort_eda import (
    get_descriptive_statistics
)


def main():

    if len(sys.argv) < 2:

        print(
            "캐릭터명을 입력해주세요."
        )

        print(
            "예:"
            " python -m "
            "backend.scripts.check_cohort_statistics "
            "박한아린"
        )

        return


    character_name = sys.argv[1]


    statistics = (
        get_descriptive_statistics(
            character_name
        )
    )


    if statistics is None:

        print(
            "Cohort 데이터를 찾을 수 없습니다."
        )

        return


    print()
    print(
        "=== LoaP Cohort 기술 통계 ==="
    )

    print()

    print(
        f"기준 캐릭터: "
        f"{character_name}"
    )

    print()

    print(
        statistics.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()