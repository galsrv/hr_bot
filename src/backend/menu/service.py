from fastapi import HTTPException, status
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from base_service import BaseService
from menu.constants import (
    ERROR_MESSAGE_BUTTON_TEXT_NAME_TAKEN,
    ERROR_MESSAGE_ENTRY_DOESNT_EXIST,
    ERROR_MESSAGE_NO_PERMISSION,
)
from menu.models import MenuOrm
from menu.schemas import (
    MenuItemCreateSchema,
    MenuItemUpdateSchema,
)
from users.models import UsersOrm
from users.service import user_service


class MenuService(BaseService):
    """Класс сервисных методов модели."""
    def __init__(self) -> None:
        super().__init__(MenuOrm)

    async def get_menu_item(
        self,
        session: AsyncSession,
        menu_item_id: int,
    ) -> MenuOrm:
        """Получаем элемент справочника по его id."""
        menu_item: MenuOrm | None = await self.get(session, menu_item_id)

        if menu_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR_MESSAGE_ENTRY_DOESNT_EXIST,
            )

        return menu_item

    async def create_menu_item(
        self, session: AsyncSession, data_input: MenuItemCreateSchema
    ) -> MenuOrm:
        """Создаем новый элемент справочника."""
        author: UsersOrm | None = await user_service.get(
            session, data_input.created_by_id
        )

        # Если указанный автор не существует или не имеет полномочий:
        if not author or not author.is_active or not author.role.can_edit_menu:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_NO_PERMISSION,
            )

        button_text_available: bool = await self._is_button_text_available(
            session, data_input.button_text
        )

        # Проверяем запрошенный текст кнопки на уникальность
        if not button_text_available:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ERROR_MESSAGE_BUTTON_TEXT_NAME_TAKEN,
            )

        data_input.updated_by_id = data_input.created_by_id
        new_menu_item = await self.create(session, data_input)
        return new_menu_item

    async def update_menu_item(
        self, session: AsyncSession, menu_item_id: int, data_input: MenuItemUpdateSchema
    ) -> MenuOrm:
        """Изменяем существующий элемент справочника."""
        menu_item: MenuOrm = await self.get(session, menu_item_id)

        editor: UsersOrm | None = await user_service.get(
            session, data_input.updated_by_id
        )

        # Если указанный автор не существует или не имеет полномочий:
        if not editor or not editor.is_active or not editor.role.can_edit_menu:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=ERROR_MESSAGE_NO_PERMISSION,
            )

        menu_item: MenuOrm = await self.update(session, menu_item, data_input)
        return menu_item

    async def delete_menu_item(
        self,
        session: AsyncSession,
        menu_item_id: int,
    ) -> None:
        """Удаляем существующий элемент справочника."""
        await self.delete(session, menu_item_id)

    async def get_menu_page(
        self,
        session: AsyncSession,
        page_params: Params = None,
    ) -> Page:
        """Получаем страницу с элементами справочника."""
        query = select(self.model).order_by(*self.model.__order_by__)
        result: Page = await apaginate(session, query, page_params)
        logger.log(
            'DB_ACCESS',
            f'Data retrieve: model={self.model.__name__}, {len(result.items)} entries retrieved',
        )
        return result

    async def _is_button_text_available(
        self,
        session: AsyncSession,
        button_text: str,
    ) -> bool:
        """Проверяем доступность запрошенного имени."""
        query = select(MenuOrm).where(MenuOrm.button_text == button_text)
        result = await session.execute(query)
        result = result.scalar_one_or_none()
        return not bool(result)


menu_service = MenuService()
