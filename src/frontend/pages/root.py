from fastapi import Depends
from nicegui import APIRouter, ui

from pages.dependencies import get_current_user
from pages.urls import (
    LOGIN_PAGE_URL,
    SETTINGS_PAGE_URL,
)
from pages.users.schemas import UserReadSchema

root_router = APIRouter()


@root_router.page('/', title='Корневая страница админки')
async def site_root_page(
    current_user: UserReadSchema = Depends(get_current_user),
) -> None:
    """Корневая страница сайта."""
    if not current_user:
        ui.navigate.to(LOGIN_PAGE_URL)

    ui.navigate.to(SETTINGS_PAGE_URL)
