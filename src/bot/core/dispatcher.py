from aiogram import Dispatcher

from handlers.help import help_router
from handlers.menu import menu_router
from handlers.message import message_router
from handlers.start import start_router

dispatcher = Dispatcher()

dispatcher.include_router(help_router)
dispatcher.include_router(menu_router)
dispatcher.include_router(start_router)
# В message_router обработка произвольного сообщения - роутер должен быть последним
dispatcher.include_router(message_router)
