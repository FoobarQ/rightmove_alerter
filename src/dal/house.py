from src.dal.user import User
from src.dal.connection import get_db_client, get_db_connection
from src.house_alerts.listing import Listing


def is_in_database(listing: Listing, user: User):
    cursor = get_db_client()
    cursor.execute(
        "SELECT id FROM house WHERE id = %s AND user_id = %s", (listing.id, user.id)
    )
    return cursor.fetchone() is not None


def add_listings_to_database(listings: list[Listing], user_id: str):
    connection = get_db_connection()
    cursor = get_db_client()

    values = [listing.to_tuple(user_id) for listing in listings]
    cursor.executemany(
        "INSERT INTO house VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", values
    )
    connection.commit()


def find_listings_to_alert(user_id: int):
    cursor = get_db_client()

    cursor.execute(
        "SELECT * from house WHERE notified = false AND user_id = %s", (user_id,)
    )
    house_rows = cursor.fetchall()

    cursor.execute("SELECT * from house WHERE user_id = %s", (user_id,))

    return [Listing(*house_row) for house_row in house_rows]
