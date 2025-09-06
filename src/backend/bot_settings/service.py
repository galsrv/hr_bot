from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from bot_settings.models import BotSettingsOrm


class BotSettingsService(BaseService):
    def __init__(self):
        super().__init__(BotSettingsOrm)

    async def setting_update(self,
                       session: AsyncSession,
                       setting: BotSettingsOrm,
                       new_value: str):
        session.add(setting)
        setting.value = new_value
        await session.commit()
        await session.refresh(setting)
        logger.log('DB_ACCESS', f'Entry update: model={setting.__class__.__name__}, id={setting.id}, updated: value={setting.value}')
        return setting

bot_settings_service = BotSettingsService()