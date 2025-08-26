from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bot_settings.models import BotSettings
from bot_settings.schemas import SettingsRead
from bot_settings.service import bot_settings_service
from database import get_async_session

botsettings_router = APIRouter()


@botsettings_router.get(
    '',
    response_model=list[SettingsRead],
    summary="Получить список настроек проекта"
)
async def get_settings(
    db: AsyncSession = Depends(get_async_session)
) -> list[BotSettings]:
    settings = await bot_settings_service.get_all(db)
    return settings # type: ignore[valid-type]