from dal.connection import get_db_client, get_db_connection


def get_search_by_id(search_id):
    cursor = get_db_client()
    cursor.execute("SELECT * from search id = %s", (search_id))
    return cursor.fetchone()


def to_url():
    pass


def get_user_searches(user_id: str):
    cursor = get_db_client()
    cursor.execute(
        "SELECT user.id FROM user INNER JOIN search ON .... WHERE user.id = %s",
        (user_id),
    )
    # TODO: MAJOR JOINS
