"""
公开 API — 学生端查看比赛信息（无需登录）
"""
import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.models.models import Competition, CompetitionStatus
from app.models.schemas import CompetitionOut, CompetitionListOut, PaginatedOut

router = APIRouter(prefix="/api/public/competitions", tags=["公开-比赛查看"])


@router.get("/", response_model=PaginatedOut, summary="比赛列表（公开）")
def list_competitions_public(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    category: str = Query(None, description="按类别筛选"),
    keyword: str = Query(None, description="标题搜索"),
    db: Session = Depends(get_db),
):
    q = db.query(Competition).filter(
        Competition.is_deleted == False,
        Competition.status == CompetitionStatus.PUBLISHED,
    )

    if category:
        q = q.filter(Competition.category == category)
    if keyword:
        q = q.filter(Competition.title.ilike(f"%{keyword}%"))

    total = q.count()
    total_pages = max(1, math.ceil(total / page_size))

    comps = (
        q.order_by(desc(Competition.registration_deadline))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [CompetitionListOut.model_validate(c) for c in comps],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/categories", summary="获取所有类别")
def list_categories(db: Session = Depends(get_db)):
    cats = (
        db.query(Competition.category)
        .filter(
            Competition.is_deleted == False,
            Competition.status == CompetitionStatus.PUBLISHED,
        )
        .distinct()
        .all()
    )
    return [c[0] for c in cats if c[0]]


@router.get("/{comp_id}", response_model=CompetitionOut, summary="比赛详情（公开）")
def get_competition_public(comp_id: int, db: Session = Depends(get_db)):
    comp = (
        db.query(Competition)
        .filter(
            Competition.id == comp_id,
            Competition.is_deleted == False,
            Competition.status == CompetitionStatus.PUBLISHED,
        )
        .first()
    )
    if not comp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="比赛不存在或未发布")

    return CompetitionOut(
        id=comp.id,
        title=comp.title,
        category=comp.category,
        description=comp.description,
        requirements=comp.requirements,
        registration_method=comp.registration_method,
        registration_url=comp.registration_url,
        registration_start=comp.registration_start,
        registration_deadline=comp.registration_deadline,
        competition_date=comp.competition_date,
        organizer=comp.organizer,
        contact_person=comp.contact_person,
        contact_phone=comp.contact_phone,
        attachment_path=comp.attachment_path,
        cover_image=comp.cover_image,
        status=comp.status.value,
        creator=None,
        created_at=comp.created_at,
        published_at=comp.published_at,
    )
