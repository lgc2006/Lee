"""
比赛管理 API — 后台 CRUD + 审核流

权限说明:
  - 录入员: 创建、编辑自己的比赛，提交审核
  - 超管: 审核通过/驳回，编辑所有比赛
  - 所有管理员: 查看比赛列表
"""
import math
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.core.database import get_db
from app.core.auth import get_current_admin, get_super_admin
from app.models.models import Admin, Competition, CompetitionStatus, AuditLog, AuditAction
from app.models.schemas import (
    CompetitionCreate, CompetitionUpdate, CompetitionOut, CompetitionListOut,
    AuditActionIn, AuditLogOut, PaginatedOut,
)

router = APIRouter(prefix="/api/competitions", tags=["比赛管理"])


# ─── 辅助函数 ──────────────────────────────────────────
def _get_or_404(db: Session, comp_id: int) -> Competition:
    comp = db.query(Competition).filter(
        Competition.id == comp_id,
        Competition.is_deleted == False,
    ).first()
    if not comp:
        raise HTTPException(status_code=404, detail="比赛不存在")
    return comp


# ─── 后台 CRUD ─────────────────────────────────────────
@router.post("/", response_model=CompetitionOut, summary="创建比赛")
def create_competition(
    body: CompetitionCreate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    comp = Competition(**body.model_dump(), creator_id=admin.id, status=CompetitionStatus.DRAFT)
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return _to_out(comp, db)


@router.get("/", response_model=PaginatedOut, summary="后台比赛列表")
def list_competitions_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    status: str = Query(None, description="按状态筛选"),
    keyword: str = Query(None, description="标题搜索"),
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    q = db.query(Competition).filter(Competition.is_deleted == False)

    if status:
        q = q.filter(Competition.status == status)
    if keyword:
        q = q.filter(Competition.title.ilike(f"%{keyword}%"))

    total = q.count()
    total_pages = max(1, math.ceil(total / page_size))

    comps = (
        q.order_by(Competition.created_at.desc())
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


@router.get("/{comp_id}", response_model=CompetitionOut, summary="比赛详情（后台）")
def get_competition_admin(
    comp_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    comp = _get_or_404(db, comp_id)
    return _to_out(comp, db)


@router.put("/{comp_id}", response_model=CompetitionOut, summary="编辑比赛")
def update_competition(
    comp_id: int,
    body: CompetitionUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    comp = _get_or_404(db, comp_id)

    # 仅创建者或超管可编辑
    if comp.creator_id != admin.id and not admin.is_super_admin:
        raise HTTPException(status_code=403, detail="仅创建者或超管可编辑")

    # 已发布的不可直接编辑（需先撤回）
    if comp.status == CompetitionStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="已发布比赛不可编辑，请先撤回")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comp, field, value)

    db.commit()
    db.refresh(comp)
    return _to_out(comp, db)


@router.delete("/{comp_id}", summary="删除比赛")
def delete_competition(
    comp_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    comp = _get_or_404(db, comp_id)
    if comp.creator_id != admin.id and not admin.is_super_admin:
        raise HTTPException(status_code=403, detail="仅创建者或超管可删除")
    comp.is_deleted = True
    db.commit()
    return {"detail": "已删除"}


# ─── 状态流转 ──────────────────────────────────────────
@router.post("/{comp_id}/submit", response_model=CompetitionOut, summary="提交审核")
def submit_for_review(
    comp_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    comp = _get_or_404(db, comp_id)
    if comp.creator_id != admin.id and not admin.is_super_admin:
        raise HTTPException(status_code=403, detail="仅创建者可提交")
    if comp.status not in (CompetitionStatus.DRAFT, CompetitionStatus.REJECTED):
        raise HTTPException(status_code=400, detail="仅草稿或驳回状态可提交审核")
    comp.status = CompetitionStatus.PENDING
    db.commit()
    db.refresh(comp)
    return _to_out(comp, db)


@router.post("/{comp_id}/recall", response_model=CompetitionOut, summary="撤回（退回草稿）")
def recall_competition(
    comp_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    comp = _get_or_404(db, comp_id)
    if comp.creator_id != admin.id and not admin.is_super_admin:
        raise HTTPException(status_code=403, detail="仅创建者可撤回")
    if comp.status not in (CompetitionStatus.PENDING, CompetitionStatus.PUBLISHED):
        raise HTTPException(status_code=400, detail="仅待审核或已发布状态可撤回")
    comp.status = CompetitionStatus.DRAFT
    db.commit()
    db.refresh(comp)
    return _to_out(comp, db)


# ─── 审核 ───────────────────────────────────────────────
@router.post("/{comp_id}/audit", response_model=CompetitionOut, summary="审核比赛（仅超管）")
def audit_competition(
    comp_id: int,
    body: AuditActionIn,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_super_admin),
):
    comp = _get_or_404(db, comp_id)
    if comp.status != CompetitionStatus.PENDING:
        raise HTTPException(status_code=400, detail="仅待审核状态可操作")

    action = AuditAction(body.action)

    if action == AuditAction.APPROVE:
        comp.status = CompetitionStatus.PUBLISHED
    else:
        comp.status = CompetitionStatus.REJECTED

    log = AuditLog(
        competition_id=comp.id,
        reviewer_id=admin.id,
        action=action,
        comment=body.comment,
    )
    db.add(log)
    db.commit()
    db.refresh(comp)
    return _to_out(comp, db)


@router.get("/{comp_id}/audit-logs", response_model=list[AuditLogOut], summary="查看审核记录")
def get_audit_logs(
    comp_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin),
):
    _get_or_404(db, comp_id)
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.competition_id == comp_id)
        .options(joinedload(AuditLog.reviewer))
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    return logs


# ─── 内部 ───────────────────────────────────────────────
def _to_out(comp: Competition, db: Session) -> CompetitionOut:
    """转响应对象（补上 creator）"""
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
        creator=comp.creator,
        created_at=comp.created_at,
        published_at=comp.published_at,
    )
