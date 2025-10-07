import asyncio
import sys

import models # noqa
from bot_settings.schemas import SettingCreateSchema
from bot_settings.service import bot_settings_service
from config import settings as s
from fixtures.service import download_data, upload_data
from menu.schemas import MenuItemCreateSchema
from menu.service import menu_service
from log import logger

async def main():
    if len(sys.argv) != 3:
        logger.warning(s.FIXTURES_MANUAL)
        sys.exit(1)

    module_arg, load_arg = sys.argv[1:3]
    if module_arg == '--settings' and load_arg == '--download':
        await download_data(bot_settings_service, s.FIXTURES_SETTINGS_PATH)
    elif module_arg == '--menu' and load_arg == '--download':
        await download_data(menu_service, s.FIXTURES_MENU_PATH)
    elif module_arg == '--settings' and load_arg == '--upload':
        await upload_data(bot_settings_service, s.FIXTURES_SETTINGS_PATH, SettingCreateSchema)
    elif module_arg == '--menu' and load_arg == '--upload':
        await upload_data(menu_service, s.FIXTURES_MENU_PATH, MenuItemCreateSchema)
    else:
        logger.warning(f'❌ Неизвестный набор аргументов: {module_arg}, {load_arg}')
        logger.warning(s.FIXTURES_MANUAL)
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())