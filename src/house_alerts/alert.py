from src.dal.house import (
    add_listings_to_database,
    find_listings_to_alert,
    is_in_database,
)
from src.dal.search import get_user_searches
from src.dal.user import get_active_users
from src.house_alerts.gmail_helper import send_emails
from src.house_alerts.scraper import get_listings_from_search
import time
import random
from src.house_alerts.listing import Listing
from src.house_alerts.constants import RIGHTMOVE_PAGE_SIZE


def get_new_listings():
    new_listings: list[Listing] = []
    for user in get_active_users():
        print(f"finding listings for {user.username}")
        for search in get_user_searches(user.id):
            all_listings_discovered = False
            index = 0
            while not all_listings_discovered:
                listings = get_listings_from_search(search.to_url(index))
                listings_not_in_database = list(
                    filter(lambda x: not is_in_database(x, user), listings)
                )
                new_listings.extend(listings_not_in_database)
                rest_time = 4.0 * random.random()
                time.sleep(rest_time)
                all_listings_discovered = (
                    len(listings_not_in_database) < RIGHTMOVE_PAGE_SIZE
                )
                index += 1

        print("adding to database")
        add_listings_to_database(new_listings, user.id)


def send_alerts():
    for user in get_active_users():
        listings = find_listings_to_alert(user.id)
        send_emails(user.email, listings)


def main():
    print("retrieving new listings")
    get_new_listings()
    print("sending alerts")
    send_alerts()
    return 0


if __name__ == "__main__":
    main()
