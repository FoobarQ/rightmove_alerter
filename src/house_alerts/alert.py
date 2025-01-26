from dal.house import add_listings_to_database, is_in_database
from dal.search import get_user_searches
from dal.user import get_active_users
from house_alerts.scraper import get_listings_from_search
import time
import random
from dotenv import load_dotenv
from src.house_alerts.listing import Listing
from src.house_alerts.constants import RIGHTMOVE_PAGE_SIZE


def main():
    new_listings: list[Listing] = []
    for user in get_active_users():
        for search in get_user_searches(user.userId):
            all_listings_discovered = False
            index = 0
            while not all_listings_discovered:
                listings = get_listings_from_search(search.to_url(index))
                listings_not_in_database = list(
                    listings.filter(lambda x: not is_in_database(x))
                )
                new_listings.extend(listings_not_in_database)
                rest_time = 4.0 * random.random()
                time.sleep(rest_time)
                all_listings_discovered = (
                    len(listings_not_in_database) < RIGHTMOVE_PAGE_SIZE
                )
                index += 1

        add_listings_to_database(new_listings, user[0])

    time.sleep(10)

    return 0


if __name__ == "__main__":
    main()
