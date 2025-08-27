import asyncio

from nicegui import ui

settings_list = [
    {'id': 1,
     'name': 'INITIAL_GREETING',
     'value': 'Уважаемый коллега! 👋🏼 Вы можете найти интересующую Вас информацию в разделах меню или написать Ваш вопрос менеджеру HR',
     'description': 'Стартовое приветствие пользователя',
     'int_type': False},
    {'id': 2,
     'name': 'TEXT_ROOT_MENU',
     'value': 'Вся информация собрана по разделам. Выберите интересующий Вас раздел 🔎',
     'description': 'Заголовок корневного меню',
     'int_type': False},
    {'id': 3,
     'name': 'INITIAL_GREETING',
     'value': 'Уважаемый коллега! 👋🏼 Вы можете найти интересующую Вас информацию в разделах меню или написать Ваш вопрос менеджеру HR',
     'description': 'Стартовое приветствие пользователя',
     'int_type': False},
    {'id': 4,
     'name': 'NUMBER_OF_PAGES',
     'value': 5,
     'description': 'Число страниц',
     'int_type': True},
]

def get_setting(id: int) -> dict | None:
    for item in settings_list:
        if item['id'] == id:
            return item

def get_settings() -> list[dict] | None:
    return settings_list

async def update_setting(id: int, new_value: str) -> dict | None:
    setting = get_setting(id)

    if not setting:
        ui.notify('Настройка не найдена!', type='negative')
        return
    
    is_valid, error_message = validate_setting(setting, new_value)

    if not is_valid:
        ui.notify(error_message, type='negative')
        return 
    
    setting['value'] = new_value if not setting['int_type'] else int(new_value)
    ui.notify('Значение сохранено!', type='positive')
    await asyncio.sleep(1)
    # ui.navigate.to(settings_page)

def validate_setting(setting, value) -> tuple[bool, str]:
    if not setting['int_type'] and len(value) > 50:
        return False, 'Значение слишком длинное'
    if setting['int_type']:
        try:
            int(value)
        except ValueError as e:
            return False, 'Значение должно быть целым числом'
        if not (1 < int(value) < 10):
            return False, 'Значение должно быть не менее 1 и не более 10'
    return True, ''