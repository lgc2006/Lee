from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth_router, competitions_router, public_router


class NoCacheMiddleware(BaseHTTPMiddleware):
    """Swagger UI 禁用缓存，避免浏览器缓存导致页面刷新循环"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.url.path in ("/docs", "/docs/", "/openapi.json"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动建表（开发环境）
    Base.metadata.create_all(bind=engine)
    # 初始化超管账号
    from app.core.database import SessionLocal
    from app.models.models import Admin
    from app.core.auth import hash_password
    db = SessionLocal()
    try:
        if not db.query(Admin).filter(Admin.username == "admin").first():
            db.add(Admin(
                username="admin",
                hashed_password=hash_password("admin123"),
                display_name="超级管理员",
                is_super_admin=True,
            ))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
)

# 禁缓存中间件（放在最外层）
app.add_middleware(NoCacheMiddleware)

# CORS — 允许前端开发服务器跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Requested-With"],
    expose_headers=["*"],
    max_age=86400,
)

# 全局 OPTIONS 兜底 — 走完 CORS 中间件后，如果还有 OPTIONS 没被路由处理，直接返回 200
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {}

# 注册路由
app.include_router(auth_router)
app.include_router(competitions_router)
app.include_router(public_router)


@app.get("/api/health", tags=["系统"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
