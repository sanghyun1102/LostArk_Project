from backend.analysis.cohort_analysis import (
    get_cohort_counts
)


def main():

    cohort_counts = (
        get_cohort_counts()
    )

    print()
    print(
        "=== LoaP Cohort 데이터 현황 ==="
    )
    print()


    if cohort_counts.empty:

        print(
            "분석 가능한 데이터가 없습니다."
        )

        return


    print(
        cohort_counts.to_string(
            index=False
        )
    )


    print()
    print(
        f"전체 Cohort 수: "
        f"{len(cohort_counts)}"
    )


if __name__ == "__main__":
    main()