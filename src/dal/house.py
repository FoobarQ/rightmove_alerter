from dal.connection import get_db_client, get_db_connection
from house_alerts.listing import Listing


def is_in_database(listing: Listing):
    cursor = get_db_client()
    cursor.execute("SELECT id FROM houses WHERE id = %s", (listing.id,))
    return cursor.fetchone() is not None


def add_listings_to_database(listings: list[Listing], user_id: str):
    connection = get_db_connection()
    cursor = get_db_client()

    values = [listing.to_tuple(user_id) for listing in listings]
    cursor.executemany("INSERT INTO classroom VALUES(%s)", values)
    connection.commit()
