from dal.connection import get_db_client


def get_active_users():
    cursor = get_db_client()
    cursor.execute("SELECT * FROM user WHERE active = true")  # TODO: actually implement
    return cursor.fetchall()
