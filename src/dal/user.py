from src.dal.connection import get_db_client


def get_active_users():
    cursor = get_db_client()
    cursor.execute('SELECT * FROM "user" WHERE active = true')
    user_rows = cursor.fetchall()

    return [User(*user_row) for user_row in user_rows]


class User:
    def __init__(self, id: int, username: str, email: str, active: bool) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.active = active
