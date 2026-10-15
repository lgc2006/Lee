"""
管理员认证 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import hash_password, verify_password, create_access_token, get_current_admin
from app.models.models import Admin
from app.models.schemas import AdminLogin, AdminCreate, AdminOut, TokenOut

router = APIRouter(prefix="/api/admin", tags=["管理员认证"])


@router.post("/login", response_model=TokenOut, summary="管理员登录")
def login(body: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(
        Admin.username == body.username,
        Admin.is_active == True,
    ).first()
    if not admin or not verify_password(body.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    token = create_access_token(data={"sub": str(admin.id)})
    return {"access_token": token, "admin": admin}


@router.post("/register", response_model=AdminOut, summary="注册管理员（需超管权限，开发阶段开放）")
def register(body: AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.username == body.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    admin = Admin(
        username=body.username,
        hashed_password=hash_password(body.password),
        display_name=body.display_name,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.get("/me", response_model=AdminOut, summary="获取当前登录信息")
def me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin
