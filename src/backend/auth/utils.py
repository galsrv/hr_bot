import secrets

import bcrypt
from auth.constants import (
    TOKEN_HEX_BASE,
)


def create_random_session_string() -> str:
    """Генерируем случайный номер сессии."""
    return secrets.token_hex(TOKEN_HEX_BASE)


def verify_password(password: str, hashed: str) -> bool:
    """Сравниваем введенный пользователем пароль с хэшем."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
