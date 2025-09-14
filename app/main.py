from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import health, ws
from app.db.session import init_db, engine
from app.core.config import get_settings
import asyncio
import uvicorn
import redis.asyncio as redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理器
    预热数据库 以及 应用结束后 关闭数据库链接等
    """
    # === 启动阶段 (Startup) ===
    startup_settings = get_settings()

    # 初始化数据库
    try:
        await init_db()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        # 可以选择抛出异常来阻止应用启动
        # raise e

    # 预热 Redis 连接
    redis_client = None
    try:
        redis_client = redis.from_url(startup_settings.redis_url, decode_responses=True)
        await redis_client.ping()
        print("✅ Redis 连接正常")

        # 将 Redis 客户端存储到应用状态中，供其他地方使用
        app.state.redis = redis_client

    except Exception as e:
        print(f"❌ Redis 连接失败: {e}")
        if redis_client:
            await redis_client.close()
        # Redis 失败不阻止应用启动，但可以设置标志
        app.state.redis = None

    print("应用启动完成")

    yield

    # === 关闭阶段 (Shutdown) ===

    # 清理 Redis 连接
    if hasattr(app.state, 'redis') and app.state.redis:
        try:
            await app.state.redis.close()
            print("✅ Redis 连接已关闭")
        except Exception as e:
            print(f"❌ Redis 关闭失败: {e}")

    # 清理数据库连接池（如果需要）
    try:
        if engine:
            await engine.dispose()
            print("✅ 数据库连接池已关闭")
    except Exception as e:
        print(f"❌ 数据库连接池关闭失败: {e}")


app = FastAPI(
    title="Realtime Editor - FastAPI scaffold",
    lifespan=lifespan
)

# 包含路由
app.include_router(health.router, prefix="/api")
app.include_router(ws.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Realtime Editor scaffold running. Health: /api/healthz, WS: /api/ws/{doc_id}",
        "redis_status": "connected" if hasattr(app.state, 'redis') and app.state.redis else "disconnected"
    }


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
