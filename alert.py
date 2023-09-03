import requests
from bs4 import BeautifulSoup
import smtplib
import time
from email.mime.text import MIMEText
import random
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(txt):
    sender = 'noreply@gmail.com'
    receivers = ['email@gmail.com']

    msg = MIMEText(txt)
    msg['Subject'] = "House Alert"
    msg['From'] = sender
    msg['To'] = ','.join(receivers)

    try:
        print("Try email")
        smtpObj = smtplib.SMTP('smtp.gmail.com')
        #smtpObj.login(sender_email, password)
        smtpObj.sendmail(sender,receivers,msg.as_string())
        print("Send email2")
    except Exception as ex:
        print("Unable to send email", ex)

EAST_LONDON = "USERDEFINEDAREA%5E%7B%22id%22%3A%228028516%22%7D"
SOUTH_LONDON = "USERDEFINEDAREA%5E%7B%22id%22%3A%228028525%22%7D"
BASE_URL = "https://www.rightmove.co.uk"
RENT_URL = f"{BASE_URL}/property-to-rent/find.html"
RIGHTMOVE_FULL_PAGE_LENGTH = 24

def rightmove_url_builder(location: str, minimum_bedrooms: int, max_price: int, dontShow: list[str]=[], radius: float = 0.0, index: int = 0):
    return f"{RENT_URL}?locationIdentifier={location}&radius={radius}&minBedrooms={minimum_bedrooms}&maxPrice={max_price}&index={index}&dontShow={'%2C'.join(dontShow)}&furnishTypes=&keywords="

def generate_is_present_function(cursor):
    def id_is_in_database(id: str):
        cursor.execute("SELECT id FROM houses WHERE id = %s", (id,))
        return cursor.fetchone() is not None
    return id_is_in_database

def find_new_listings(search_url: str, id_is_in_database):
    new_listings = []

    search_response = requests.get(search_url)
    found_all_properties = not search_response.ok
    if found_all_properties:
        return new_listings
    
    soup = BeautifulSoup(search_response.text, 'html.parser')
    html = soup.find_all("div", {"class": "propertyCard-wrapper"})

    property_count = len(html)
    found_all_properties = property_count == 0
    if (found_all_properties):    
        return new_listings

    for element in html[1:]:    #   skip the promoted ad at the top
        description_element = element.find("div", {"class": "propertyCard-description"})
        relative_url: str = description_element.find("a").get('href')
        ad_url = f"{BASE_URL}{relative_url}"
        url_parts = relative_url.replace("#", "").split("/")
        found_all_properties = len(url_parts) < 2

        if (found_all_properties):
            return new_listings

        id = url_parts[2]
        description: str = description_element.find("span").get_text()

        price: str = element.find("span", {"class": 'propertyCard-priceValue'}).get_text()
        price = price.replace(",", "").replace("£", "").replace("pcm", "")
        price = int(price)

        address = element.find("address")
        street_address: str = address.find("span").get_text()
        country_code: str = address.find("meta", {"itemprop": 'addressCountry'}).get("content")

        title: str = element.find("h2", {"class": "propertyCard-title"}).get_text()
        title = title.strip()

        if id_is_in_database(id):
            return new_listings
        else:
            new_listings.append({
                "id": id,
                "listing_title": title,
                "street_address": street_address,
                "price": price,
                "description": description,
                "url": ad_url,
                "country": country_code
            })
        
    return new_listings

def main():
    database = os.getenv("DATABASE_NAME")
    user = os.getenv("DATABASE_USERNAME")
    password = os.getenv("DATABASE_PASSWORD")
    port = os.getenv("DATABASE_PORT")
    host = os.getenv("DATABASE_HOST")

    if (not database or not user or not password or not host or not port):
        print("Database options not filled")
        return -1
    
    connection = psycopg2.connect(user=user, password=password, database=database, host=host)
    cursor = connection.cursor()
    id_is_in_database = generate_is_present_function(cursor=cursor)

    places = {
        "South London": SOUTH_LONDON,
        "East London": EAST_LONDON
    }

    for area, location in places.items():
        index = 0
        all_listings_discovered = False

        while not all_listings_discovered:
            url = rightmove_url_builder(location=location, minimum_bedrooms=2, max_price=2500, dontShow=["retirement", "student", "houseShare"], index=index)
            new_listings = find_new_listings(url, id_is_in_database)
            all_listings_discovered = len(new_listings) < RIGHTMOVE_FULL_PAGE_LENGTH
            index += len(new_listings)
            rest_time = 4.0 * random.random()
            time.sleep(rest_time)
            
        print(f"found {index} properties in {area}")

    return 0

main()