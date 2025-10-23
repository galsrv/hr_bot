from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bot_settings.models import BotSettingsOrm
from bot_settings.schemas import (
    SettingCreateSchema,
    SettingsChangeSchema,
    SettingsReadSchema,
)
from bot_settings.service import bot_settings_service
from config import settings as s
from database import get_async_session

botsettings_router = APIRouter()


@botsettings_router.get(
    '/',
    response_model=list[SettingsReadSchema],
    summary='Получить список настроек проекта',
)
async def get_settings(
    session: AsyncSession = Depends(get_async_session),
) -> list[SettingsReadSchema]:
    """Эндпоинт получения всех настроек проекта."""
    settings = await bot_settings_service.get_all(session)
    return settings


@botsettings_router.get(
    '/{setting_id}', response_model=SettingsReadSchema, summary='Получить настройку проекта'
)
async def get_one_setting(
    setting_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> SettingsReadSchema:
    """Эндпоинт получения одной настройки проекта."""
    setting: BotSettingsOrm | None = await bot_settings_service.get_setting(session, setting_id)
    return setting


@botsettings_router.patch(
    '/{setting_id}', response_model=SettingsReadSchema, summary='Изменить настройку проекта'
)
async def change_setting(
    setting_id: int,
    data_input: SettingsChangeSchema,
    session: AsyncSession = Depends(get_async_session),
) -> SettingsReadSchema:
    """Эндпоинт изменения настройки проекта."""
    setting = await bot_settings_service.update_setting(session, setting_id, data_input)
    return setting


@botsettings_router.post(
    '/download', response_model=None, summary='Выгрузить настройки проекта в файл'
)
async def download_settings(
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Эндпоинт выгрузки настроек проекта в файл."""
    await bot_settings_service.download_data(session, s.FIXTURES_SETTINGS_PATH)


@botsettings_router.post(
    '/upload', response_model=None, summary='Загрузить настройки проекта из файла'
)
async def upload_settings(
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Эндпоинт загрузки настроек из файла."""
    await bot_settings_service.upload_data(
        session, s.FIXTURES_SETTINGS_PATH, SettingCreateSchema
    )
