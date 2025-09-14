import bcrypt
import secrets

from users.constants import TOKEN_HEX_BASE

def hash_password(password: str) -> str:
    '''Хэшируем введенный пользователем пароль.'''
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    '''Сравниваем введенный пользователем пароль с хэшем.'''
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_random_session_string() -> str:
    '''Генерируем случайный номер сессии.'''
    return secrets.token_hex(TOKEN_HEX_BASE)
