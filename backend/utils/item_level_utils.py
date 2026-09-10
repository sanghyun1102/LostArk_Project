import math


def get_item_level_band(
    item_level,
    band_size=5
):
    """
    아이템 레벨을 고정된 구간으로 나눈다.

    예:
    1732.50
    → 1730 <= level < 1735

    1737.50
    → 1735 <= level < 1740
    """

    if item_level is None:
        return None

    start = (
        math.floor(
            item_level / band_size
        )
        * band_size
    )

    end = start + band_size

    return {
        "start": start,
        "end": end,
        "display_end": round(
            end - 0.01,
            2
        )
    }