"""
Pydantic schemas — 请求/响应数据校验
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════
# Admin
# ═══════════════════════════════════════════════════════
class AdminLogin(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str = Field(..., min_length=1, max_length=64)


class AdminOut(BaseModel):
    id: int
    username: str
    display_name: str
    is_super_admin: bool

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminOut


# ═══════════════════════════════════════════════════════
# Competition
# ═══════════════════════════════════════════════════════
class CompetitionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=256)
    category: str = Field(..., min_length=1, max_length=64)
    description: str = Field(..., min_length=1)
    requirements: Optional[str] = None
    registration_method: Optional[str] = None
    registration_url: Optional[str] = None
    registration_start: Optional[datetime] = None
    registration_deadline: datetime
    competition_date: Optional[datetime] = None
    organizer: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class CompetitionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=256)
    category: Optional[str] = Field(None, min_length=1, max_length=64)
    description: Optional[str] = None
    requirements: Optional[str] = None
    registration_method: Optional[str] = None
    registration_url: Optional[str] = None
    registration_start: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    competition_date: Optional[datetime] = None
    organizer: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None


class CompetitionOut(BaseModel):
    id: int
    title: str
    category: str
    description: str
    requirements: Optional[str]
    registration_method: Optional[str]
    registration_url: Optional[str]
    registration_start: Optional[datetime]
    registration_deadline: datetime
    competition_date: Optional[datetime]
    organizer: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    attachment_path: Optional[str]
    cover_image: Optional[str]
    status: str
    creator: Optional[AdminOut]
    created_at: datetime
    published_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CompetitionListOut(BaseModel):
    """列表页（缩略）"""
    id: int
    title: str
    category: str
    registration_deadline: datetime
    status: str
    organizer: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════
# Audit
# ═══════════════════════════════════════════════════════
class AuditActionIn(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    comment: Optional[str] = None


class AuditLogOut(BaseModel):
    id: int
    action: str
    comment: Optional[str]
    reviewer: Optional[AdminOut]
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════
# 分页
# ═══════════════════════════════════════════════════════
class PaginatedOut(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
