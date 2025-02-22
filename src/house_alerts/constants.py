from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "https://www.rightmove.co.uk"
RENT_URL = f"{BASE_URL}/property-to-rent/find.html"
RIGHTMOVE_PAGE_SIZE = 24
SENDER = os.getenv("FROM_SENDER")
