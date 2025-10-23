import bcrypt


def hash_password(password: str) -> str:
    """Хэшируем введенный пользователем пароль."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
