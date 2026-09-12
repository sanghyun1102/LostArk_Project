import sys

import pandas as pd

from backend.analysis.cohort_eda import (
    get_feature_quality_report
)


def main():

    if len(sys.argv) < 2:

        print(
            "캐릭터명을 입력해주세요."
        )

        print(
            "예:"
            " python -m "
            "backend.scripts.check_cohort_quality "
            "박한아린"
        )

        return


    character_name = sys.argv[1]


    result = (
        get_feature_quality_report(
            character_name
        )
    )


    if result is None:

        print(
            "Cohort 데이터를 찾을 수 없습니다."
        )

        return


    cohort = result["cohort"]

    quality_dataframe = (
        pd.DataFrame(
            result["quality"]
        )
    )


    print()
    print(
        "=== LoaP Cohort 품질 확인 ==="
    )

    print()

    print(
        f"기준 캐릭터: "
        f"{character_name}"
    )

    print(
        f"Cohort 크기: "
        f"{len(cohort)}"
    )


    print()
    print(
        "=== Feature 결측치 현황 ==="
    )

    print()

    print(
        quality_dataframe
        .to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()