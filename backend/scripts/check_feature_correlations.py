import sys

from backend.analysis.cohort_eda import (
    get_feature_correlations
)


def main():

    if len(sys.argv) < 2:

        print(
            "캐릭터명을 입력해주세요."
        )

        return


    character_name = sys.argv[1]


    correlations = (
        get_feature_correlations(
            character_name
        )
    )


    if correlations is None:

        print(
            "Cohort 데이터를 찾을 수 없습니다."
        )

        return


    print()
    print(
        "=== LoaP Feature 상관관계 ==="
    )

    print()

    print(
        correlations.to_string()
    )


if __name__ == "__main__":
    main()