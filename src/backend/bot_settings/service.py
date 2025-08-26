from base_service import BaseService
from bot_settings.models import BotSettings


class BotSettingsService(BaseService):
    def __init__(self):
        super().__init__(BotSettings)


bot_settings_service = BotSettingsService()