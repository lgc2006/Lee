from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "比赛查询系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库 (默认用SQLite开发，上线切PostgreSQL)
    DATABASE_URL: str = "sqlite:///./competition.db"

    # JWT
    SECRET_KEY: str = "change-me-to-a-random-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8小时

    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
