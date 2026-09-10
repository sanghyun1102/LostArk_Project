from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.collectors.collect_character import collect_character
from backend.services.snapshot_service import save_character_snapshot
from backend.db.database import create_tables
from backend.services.growth_service import (
    get_latest_growth,
    get_growth_history
)
from backend.services.comparison_service import (
    get_comparison_cohort
)
from backend.services.candidate_service import (
    find_candidates
)

app = FastAPI()

create_tables()

# CSS 등 정적 파일
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# HTML 템플릿 폴더
templates = Jinja2Templates(
    directory="templates"
)


# ==============================
# 메인 페이지
# ==============================

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ==============================
# 캐릭터 검색 결과 페이지
# ==============================

@app.get(
    "/character/{character_name}",
    response_class=HTMLResponse
)
def character(
    request: Request,
    character_name: str
):

    character_data = collect_character(
        character_name
    )

    if not character_data:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "캐릭터 정보를 찾을 수 없습니다."
            }
        )

    save_character_snapshot(
        character_data
    )

    # ==============================
    # 방어구 정리
    # ==============================

    armor_by_type = {
        item.get("type"): item
        for item in character_data.get(
            "armor",
            []
        )
    }

    # ==============================
    # 액세서리 정리
    # ==============================

    accessories = character_data.get(
        "accessories",
        []
    )

    necklace = next(
        (
            item
            for item in accessories
            if item.get("type") == "목걸이"
        ),
        None
    )

    earrings = [
        item
        for item in accessories
        if item.get("type") == "귀걸이"
    ]

    rings = [
        item
        for item in accessories
        if item.get("type") == "반지"
    ]
    
    # ==============================
    # 스킬 보석 정리
    # ==============================

    skill_gems = (
        character_data
        .get("skill_gems", {})
        .get("gems", [])
    )


    def sort_gems(gems):
        return sorted(
            gems,
            key=lambda gem: (
                -(gem.get("level") or 0),
                gem.get("skill_name") or ""
            )
        )


    gem_groups = {
        "겁화": sort_gems([
            gem
            for gem in skill_gems
            if gem.get("type") == "겁화"
        ]),

        "작열": sort_gems([
            gem
            for gem in skill_gems
            if gem.get("type") == "작열"
        ]),

        "광휘": sort_gems([
            gem
            for gem in skill_gems
            if gem.get("type") == "광휘"
        ])
    }

    return templates.TemplateResponse(
        request=request,
        name="character.html",
        context={
            "character": character_data,
            "armor": armor_by_type,
            "necklace": necklace,
            "earrings": earrings,
            "rings": rings,
            "gem_groups": gem_groups
        }
    )

@app.get(
    "/api/characters/{character_name}/growth"
)
def character_growth(
    character_name: str
):

    return get_latest_growth(
        character_name
    )

@app.get(
    "/api/characters/{character_name}/history"
)
def character_history(
    character_name: str
):

    return get_growth_history(
        character_name
    )

@app.get(
    "/api/characters/{character_name}/cohort"
)
def character_cohort(
    character_name: str
):

    return get_comparison_cohort(
        character_name
    )

@app.get(
    "/api/characters/{character_name}/candidates"
)
def character_candidates(
    character_name: str
):

    return find_candidates(
        character_name
    )