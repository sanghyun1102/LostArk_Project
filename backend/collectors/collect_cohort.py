import sys
import time

from backend.services.candidate_service import (
    find_candidates
)
from backend.collectors.collect_character import (
    collect_character
)
from backend.services.snapshot_service import (
    save_character_snapshot
)
from backend.services.comparison_service import (
    get_build_name,
    get_latest_snapshot
)
from backend.db.database import SessionLocal
from backend.db.models import Character

from sqlalchemy import select


def get_target_build(
    character_name
):
    """
    기준 캐릭터의 최신 Snapshot에서
    빌드명을 가져온다.
    """

    with SessionLocal() as db:

        character = db.scalar(
            select(Character)
            .where(
                Character.character_name
                == character_name
            )
        )

        if character is None:
            return None

        snapshot = get_latest_snapshot(
            db,
            character.id
        )

        if snapshot is None:
            return None

        return get_build_name(
            snapshot
        )


def collect_cohort_candidates(
    character_name
):
    """
    기준 캐릭터와

    - 같은 클래스
    - 같은 5레벨 구간

    후보들을 상세 수집한 뒤
    같은 빌드만 비교 집단으로 분류한다.
    """

    # ==============================
    # 기준 빌드 확인
    # ==============================

    target_build = get_target_build(
        character_name
    )

    if target_build is None:

        print(
            "기준 캐릭터의 빌드를 "
            "확인할 수 없습니다."
        )

        return


    # ==============================
    # 1차 후보 조회
    # ==============================

    candidate_result = find_candidates(
        character_name
    )

    if (
        candidate_result.get("status")
        != "ok"
    ):

        print(
            candidate_result.get(
                "message",
                "후보 조회 실패"
            )
        )

        return


    candidates = candidate_result.get(
        "candidates",
        []
    )


    print()
    print("=" * 50)

    print(
        f"기준 캐릭터: "
        f"{character_name}"
    )

    print(
        f"기준 빌드: "
        f"{target_build}"
    )

    item_level_band = (
        candidate_result.get(
            "item_level_band",
            {}
        )
    )

    print(
        f"아이템 레벨 구간: "
        f"{item_level_band.get('start')}"
        f" ~ "
        f"{item_level_band.get('end')}"
    )

    print(
        f"1차 후보: "
        f"{len(candidates)}명"
    )

    print("=" * 50)


    if not candidates:

        print(
            "수집할 후보가 없습니다."
        )

        return


    # ==============================
    # 결과 카운트
    # ==============================

    same_build = []

    different_build = []

    fail_count = 0


    # ==============================
    # 후보 상세 수집
    # ==============================

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        candidate_name = (
            candidate.get(
                "character_name"
            )
        )

        print()
        print(
            f"[{index}/{len(candidates)}] "
            f"{candidate_name}"
        )


        try:

            # ==============================
            # 이미 DB에 저장된 캐릭터인지 확인
            # ==============================

            with SessionLocal() as db:

                saved_character = db.scalar(
                    select(Character)
                    .where(
                        Character.character_name
                        == candidate_name
                    )
                )

                saved_snapshot = None

                if saved_character:

                    saved_snapshot = (
                        get_latest_snapshot(
                            db,
                            saved_character.id
                        )
                    )


            # ==============================
            # 기존 Snapshot이 있으면 재사용
            # ==============================

            if saved_snapshot:

                character_data = (
                    saved_snapshot.processed_data
                )

                print(
                   "기존 DB 데이터 사용"
                )


            # ==============================
            # 없으면 API에서 새로 수집
            # ==============================

            else:

                character_data = (
                    collect_character(
                        candidate_name
                    )
                )

                if not character_data:

                    print(
                        "상세 데이터 없음"
                    )

                    fail_count += 1
                    continue

                save_character_snapshot(
                    character_data
                )

                time.sleep(0.7)

            if not character_data:

                print(
                    "상세 데이터 없음"
                )

                fail_count += 1
                continue


            # DB Snapshot 저장
            save_character_snapshot(
                character_data
            )


            # ==============================
            # 빌드 확인
            # ==============================

            ark_passive = (
                character_data.get(
                    "ark_passive"
                )
                or {}
            )

            candidate_build = (
                ark_passive.get(
                    "title"
                )
            )


            if candidate_build == target_build:

                same_build.append({
                    "character_name":
                        candidate_name,

                    "build_name":
                        candidate_build,

                    "item_level":
                        character_data[
                            "profile"
                        ].get(
                            "item_level"
                        )
                })

                print(
                    f"비교 대상 포함: "
                    f"{candidate_build}"
                )


            else:

                different_build.append({
                    "character_name":
                        candidate_name,

                    "build_name":
                        candidate_build
                })

                print(
                    f"다른 빌드 제외: "
                    f"{candidate_build}"
                )


        except Exception as error:

            print(
                f"수집 실패: "
                f"{candidate_name}"
            )

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

            fail_count += 1

            continue


    # ==============================
    # 결과
    # ==============================

    print()
    print("=" * 50)

    print("비교 집단 수집 완료")

    print(
        f"같은 빌드: "
        f"{len(same_build)}명"
    )

    print(
        f"다른 빌드: "
        f"{len(different_build)}명"
    )

    print(
        f"수집 실패: "
        f"{fail_count}명"
    )


    if same_build:

        print()
        print(
            f"=== {target_build} 비교 대상 ==="
        )

        for character in same_build:

            print(
                f"{character['character_name']}"
                f" | "
                f"Lv.{character['item_level']}"
            )


def main():

    if len(sys.argv) < 2:

        print(
            "사용법: "
            "python -m backend.collect_cohort "
            "캐릭터이름"
        )

        return


    character_name = (
        sys.argv[1]
    )

    collect_cohort_candidates(
        character_name
    )


if __name__ == "__main__":
    main()