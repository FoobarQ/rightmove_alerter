from src.house_alerts.constants import RENT_URL
from src.dal.connection import get_db_client


def get_search_by_id(search_id):
    cursor = get_db_client()
    cursor.execute("SELECT * from search id = %s", (search_id))
    return cursor.fetchone()


def get_user_searches(user_id: int):

    cursor = get_db_client()
    cursor.execute(
        """
        SELECT location_identifier, name, house_share, retirement_home, student_accomodation, garden, parking, minimum_beds, maximum_beds, student_hall, furnished, unfurnished, part_furnished
        FROM search
        INNER JOIN "location" ON search.location_id=location.id
        INNER JOIN "criteria" ON search.criteria_id=criteria.id
        WHERE search.user_id = %s;""",
        [user_id],
    )
    search_rows = cursor.fetchall()
    return [Search(*search_row) for search_row in search_rows]


class Search:
    def __init__(
        self,
        location_id,
        location_name,
        house_share,
        retirement_home,
        student_accomodation,
        garden,
        parking,
        minimum_beds,
        maximum_beds,
        student_hall,
        furnished,
        unfurnished,
        part_furnished,
    ):
        self.location_id = location_id
        self.location_name = location_name
        self.house_share = bool(house_share)
        self.retirement_home = bool(retirement_home)
        self.student_accomodation = bool(student_accomodation)
        self.garden = garden
        self.parking = parking
        self.minimum_beds = minimum_beds
        self.maximum_beds = maximum_beds
        self.student_hall = student_hall
        self.furnished = furnished
        self.unfurnished = unfurnished
        self.part_furnished = part_furnished

    def to_url(self, index):
        return f"{RENT_URL}?useLocationIdentifier=true&locationIdentifier={self.location_id}&rent=To+rent&radius=0.25&maxPrice={2500}&minBedrooms={self.minimum_beds}&index={index}"


# https://www.rightmove.co.uk/property-to-rent/find.html?searchLocation=Zone+2%2C+London&useLocationIdentifier=true&locationIdentifier=REGION%5E93814&rent=To+rent&radius=0.25&maxPrice=2250&minBedrooms=3&_includeLetAgreed=on&includeLetAgreed=false
