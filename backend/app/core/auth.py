"""
JWT 认证工具
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.models import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")


def hash_password(password: str) -> str:
    """PBKDF2-SHA256 哈希，格式: salt$hash"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 600_000)
    return f"{salt}${hashed.hex()}"


def verify_password(plain: str, stored: str) -> bool:
    salt, hashed = stored.split("$", 1)
    return hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 600_000).hex() == hashed


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    """从 JWT 中解析当前登录的管理员"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_id = int(payload.get("sub"))
        if admin_id is None:
            raise credentials_exception
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.id == admin_id, Admin.is_active == True).first()
    if admin is None:
        raise credentials_exception
    return admin


def get_super_admin(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    """仅超级管理员可调用"""
    if not current_admin.is_super_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅超级管理员可执行此操作")
    return current_admin
