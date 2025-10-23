import asyncio
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from loguru import logger
from sqlalchemy import delete, or_

from auth.constants import SESSION_CLEANUP_FREQ_IN_HOURS
from auth.models import SessionsOrm
from database import AsyncSessionLocal


async def cleanup_sessions_task():
    """Чистим сессии с заданной периодичностью, сессии заблокированных пользователей и просроченные."""
    while True:
        async with AsyncSessionLocal() as session:
            try:
                stmt = delete(SessionsOrm).where(
                    or_(
                        SessionsOrm.user.has(is_active=False),
                        SessionsOrm.expired_at < datetime.now(),
                    )
                )
                await session.execute(stmt)
                await session.commit()
                logger.log(
                    'DB_ACCESS',
                    f'Data deletion: model={SessionsOrm.__name__}, expired sessions removed',
                )
            except Exception as e:
                logger.log(
                    'DB_ACCESS',
                    f'Data deletion: model={SessionsOrm.__name__}, error: {e}',
                )

            await asyncio.sleep(SESSION_CLEANUP_FREQ_IN_HOURS * 60 * 60)


@asynccontextmanager
async def lifespan_tasks(app: FastAPI):
    task = asyncio.create_task(cleanup_sessions_task())
    try:
        yield
    finally:
        task.cancel()
