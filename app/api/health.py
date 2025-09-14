from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import async_session, engine
from app.core.config import settings
import asyncio
import redis.asyncio as redis

router = APIRouter()


@router.get("/healthz")
async def healthz():
    # DB check
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        return {"status": "fail", "db": False, "error": str(e)}

    # Redis check
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
        pong = await r.ping()
        await r.close()
        if not pong:
            raise RuntimeError("redis ping failed")
    except Exception as e:
        return {"status": "fail", "redis": False, "error": str(e)}

    return {"status": "ok", "db": True, "redis": True}
