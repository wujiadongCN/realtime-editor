# app/core/config.py
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent.parent
# if os.getenv("RUNNING_IN_DOCKER"):
#     load_dotenv(ROOT / ".env.docker")
# else:
load_dotenv(ROOT / ".env")

class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    app_name: str = "Realtime Editor API"
    debug: bool = False
    version: str = "1.0.0"

    # 服务器配置
    host: str = Field(default="0.0.0.0", alias="APP_HOST")
    port: int = Field(default=8000, alias="APP_PORT")

    # 数据库配置
    database_url: str = Field(..., alias="DATABASE_URL")

    # Redis 配置
    redis_url: str = Field(..., alias="REDIS_URL")

    # 可选的详细数据库配置（如果需要单独访问）
    postgres_user: Optional[str] = Field(default=None, alias="POSTGRES_USER")
    postgres_password: Optional[str] = Field(default=None, alias="POSTGRES_PASSWORD")
    postgres_db: Optional[str] = Field(default=None, alias="POSTGRES_DB")
    postgres_host: Optional[str] = Field(default=None, alias="POSTGRES_HOST")
    postgres_port: Optional[int] = Field(default=None, alias="POSTGRES_PORT")

    # 安全配置
    secret_key: str = Field(default="your-secret-key-change-in-production")
    access_token_expire_minutes: int = 30

    # CORS 配置
    cors_origins: str = Field(default="*")

    model_config = SettingsConfigDict(
        # 忽略未定义的环境变量
        extra="ignore",
        # 环境变量名大小写敏感
        case_sensitive=True,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """获取 CORS 允许的源列表"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.debug


@lru_cache()
def get_settings() -> Settings:
    """
    获取设置实例（带缓存）
    使用 @lru_cache 确保只创建一次实例，避免重复读取 .env 文件
    """
    return Settings()


# 全局设置实例（可选，用于非依赖注入场景）
settings = get_settings()
