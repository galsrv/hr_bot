from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from bot_settings.models import BotSettingsOrm
from bot_settings.schemas import SettingsRead, SettingsChange, SettingsChangeValidated
from bot_settings.service import bot_settings_service
from database import get_async_session

botsettings_router = APIRouter()


@botsettings_router.get(
    '',
    response_model=list[SettingsRead],
    summary="Получить список настроек проекта"
)
async def get_settings(
    session: AsyncSession = Depends(get_async_session)
) -> list[BotSettingsOrm]:
    settings = await bot_settings_service.get_all(session)
    return settings

@botsettings_router.get(
    '/{id}',
    response_model=SettingsRead,
    summary="Получить одну настройку проекта"
)
async def get_one_setting(
    id: int,
    session: AsyncSession = Depends(get_async_session),
) -> BotSettingsOrm | None:
    setting: BotSettingsOrm | None = await bot_settings_service.get(session, id)

    if setting is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Запрошенная настройка не существует'
        )

    return setting

@botsettings_router.patch(
    '/{id}',
    response_model=SettingsRead,
    summary="Изменить настройку проекта"
)
async def change_setting(
    id: int,
    new_data: SettingsChange,
    session: AsyncSession = Depends(get_async_session),
) -> BotSettingsOrm | None:
    setting: BotSettingsOrm  = await get_one_setting(id, session)

    try:
        setting_validated = SettingsChangeValidated(value=new_data.value, int_type=setting.int_type)
    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ve.errors(include_context=False)
        )

    setting = await bot_settings_service.setting_update(session, setting, setting_validated.value)
    return setting