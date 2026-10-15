"""
数据库模型

实体关系:
  Admin 1──N Competition (录入人)
  Admin 1──N AuditLog  (审核人)
  Competition 1──N AuditLog (审核记录)
"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    Enum, ForeignKey, func,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


# ─── 枚举 ─────────────────────────────────────────────
class CompetitionStatus(str, enum.Enum):
    DRAFT = "draft"          # 草稿
    PENDING = "pending"      # 待审核
    PUBLISHED = "published"  # 已发布
    REJECTED = "rejected"    # 已驳回
    CLOSED = "closed"        # 已截止


class AuditAction(str, enum.Enum):
    APPROVE = "approve"      # 通过
    REJECT = "reject"        # 驳回
    RECALL = "recall"        # 撤回


# ─── 管理员 ────────────────────────────────────────────
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(String(256), nullable=False)
    display_name = Column(String(64), nullable=False)
    is_super_admin = Column(Boolean, default=False)  # 超管可审批
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    competitions = relationship("Competition", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="reviewer")


# ─── 竞赛 ──────────────────────────────────────────────
class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False, comment="赛事名称")
    category = Column(String(64), nullable=False, comment="类别:学科竞赛/创新创业/文体活动/社会实践/其他")

    # 详细介绍
    description = Column(Text, nullable=False, comment="赛事介绍-富文本")
    requirements = Column(Text, comment="参赛要求-富文本")
    registration_method = Column(Text, comment="报名方式")
    registration_url = Column(String(512), comment="报名链接")

    # 时间
    registration_start = Column(DateTime, comment="报名开始时间")
    registration_deadline = Column(DateTime, nullable=False, comment="报名截止时间")
    competition_date = Column(DateTime, comment="比赛时间")

    # 组织信息
    organizer = Column(String(256), comment="主办单位")
    contact_person = Column(String(64), comment="联系人")
    contact_phone = Column(String(32), comment="联系电话")

    # 附件
    attachment_path = Column(String(512), comment="附件路径")
    cover_image = Column(String(512), comment="封面图路径")

    # 状态与审核
    status = Column(
        Enum(CompetitionStatus),
        default=CompetitionStatus.DRAFT,
        nullable=False,
        index=True,
        comment="发布状态",
    )

    # 关联
    creator_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime, comment="发布时间")

    # 软删除
    is_deleted = Column(Boolean, default=False)

    # 关系
    creator = relationship("Admin", back_populates="competitions")
    audit_logs = relationship("AuditLog", back_populates="competition", order_by="AuditLog.created_at.desc()")


# ─── 审核记录 ──────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False, index=True)
    reviewer_id = Column(Integer, ForeignKey("admins.id"), nullable=False)

    action = Column(Enum(AuditAction), nullable=False)
    comment = Column(Text, comment="审核意见/驳回理由")
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    competition = relationship("Competition", back_populates="audit_logs")
    reviewer = relationship("Admin", back_populates="audit_logs")
