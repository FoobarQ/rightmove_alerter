import sys
import requests
from bs4 import BeautifulSoup
import time
import random
import psycopg2
import os
from dotenv import load_dotenv
from src.house_alerts.gmail_helper import get_gmail_credentials, send_email

load_dotenv()
EAST_LONDON = "USERDEFINEDAREA%5E%7B%22id%22%3A%228028516%22%7D"
SOUTH_LONDON = "USERDEFINEDAREA%5E%7B%22id%22%3A%228028525%22%7D"
new_area = "USERDEFINEDAREA%5E%7B%22id%22%3A8028516%7D"
BASE_URL = "https://www.rightmove.co.uk"
RENT_URL = f"{BASE_URL}/property-to-rent/find.html"
RIGHTMOVE_FULL_PAGE_LENGTH = 24

class Listing:
    def __init__(self, id: str, listing_title: str, price: int, description: str, listing_url: str, country: str, street_address: str, image_url: str ) -> None:
        self.id = id
        self.listing_title = listing_title
        self.price = price
        self.description = description
        self.listing_url = listing_url
        self.country = country
        self.street_address = street_address
        self.image_url = image_url
    
    def insert_statement(self):
        query = "INSERT INTO houses(id, listing_title, country, street_address, price, description, url, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        args_tuple = (self.id, self.listing_title, self.country, self.street_address, self.price, self.description, self.listing_url, self.image_url)
        return query, args_tuple
    
    def create_email_row(self):
        return f"""
            <tr>
                <td class="image">
                    <img src="{self.image_url}"/>
                </td>
                <td>
                    <div>
                        <h2>
                            <a href="{self.listing_url}">{self.listing_title}</a>
                        </h2>
                        <h5>{self.street_address} ({self.price})</h5>
                        <p style="word-break">{self.description}</p>
                    </div>
                </td>
            </tr>
            """
    
    def create_email_body(self):
        return f"""
        <html>
            <head>
                <style>
                    .image {{
                        width: 100px;
                        padding: 20px;
                    }}
                    @media screen and (min-width: 1200px) {{
                        .image {{
                            width: 600px;
                            padding: 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <table>
                    <tbody>
                        <tr>
                            <td class="image">
                                <img src="{self.image_url}"/>
                            </td>
                            <td>
                                <div>
                                    <h2>
                                        <a href="{self.listing_url}">{self.listing_title}</a>
                                    </h2>
                                    <h5>{self.street_address} ({self.price})</h5>
                                    <p style="word-break">{self.description}</p>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """

    def __str__(self):
        return f"""
        id:             {self.id}
        title:          {self.listing_title}
        street address: {self.street_address}
        country:        {self.country}
        price:          {self.price}
        description:    {self.description}
        url:            {self.listing_url}
        image_url:      {self.image_url}
        """

def rightmove_url_builder(location: str, minimum_bedrooms: int, max_price: int, dontShow: list[str]=[], radius: float = 0.0, index: int = 0):
    return f"{RENT_URL}?locationIdentifier={location}&radius={radius}&minBedrooms={minimum_bedrooms}&maxPrice={max_price}&index={index}&dontShow={'%2C'.join(dontShow)}&furnishTypes=&keywords="

def generate_is_present_function(cursor):
    def id_is_in_database(id: str):
        cursor.execute("SELECT id FROM houses WHERE id = %s", (id,))
        return cursor.fetchone() is not None
    return id_is_in_database

def find_new_listings(search_url: str, id_is_in_database):
    new_listings = []
    property_count = 0

    search_response = requests.get(search_url)
    found_all_properties = not search_response.ok
    if found_all_properties:
        return new_listings, property_count
    soup = BeautifulSoup(search_response.text, 'html.parser')
    html = soup.find_all("div", {"class": "propertyCard-wrapper"})

    found_all_properties = len(html) == 0
    if (found_all_properties):    
        return new_listings, property_count
    
    for element in html[1:]:    #   skip the promoted ad at the top
        description_element = element.find("div", {"class": "propertyCard-description"})
        relative_url: str = description_element.find("a").get('href')
        ad_url = f"{BASE_URL}{relative_url}"
        url_parts = relative_url.replace("#", "").split("/")
        found_all_properties = len(url_parts) < 2

        if (found_all_properties):
            return new_listings, property_count

        id = url_parts[2]
        description: str = description_element.find("span").get_text()
        image_url: str = element.find("img", {"itemprop": "image"}).get("src")

        price: str = element.find("span", {"class": 'propertyCard-priceValue'}).get_text()
        price = price.replace(",", "").replace("£", "").replace("pcm", "")
        price = int(price)

        address = element.find("address")
        street_address: str = address.find("span").get_text()
        country_code: str = address.find("meta", {"itemprop": 'addressCountry'}).get("content")

        title: str = element.find("h2", {"class": "propertyCard-title"}).get_text()
        title = title.strip()

        current_listing = Listing(id=id, listing_title=title, price=price, description=description, listing_url=ad_url, country=country_code, street_address=street_address, image_url=image_url)
        property_count += 1
        
        if id_is_in_database(id):
            continue
        else:
            new_listings.append(current_listing)
        
    return new_listings, property_count

def main():
    database = os.getenv("DATABASE_NAME")
    user = os.getenv("DATABASE_USERNAME")
    password = os.getenv("DATABASE_PASSWORD")
    port = os.getenv("DATABASE_PORT")
    host = os.getenv("DATABASE_HOST")
    to = os.getenv("TO")
    sender = os.getenv("FROM_SENDER")
    creds = get_gmail_credentials()

    if (not database or not user or not password or not host or not port):
        print("Database options not filled")
        return -1
    
    connection = psycopg2.connect(user=user, password=password, database=database, host=host)
    cursor = connection.cursor()
    id_is_in_database = generate_is_present_function(cursor=cursor)

    places = {
        # "South London": SOUTH_LONDON,
        # "East London": EAST_LONDON,
        "THE AREA I ACTUALLY WANT": new_area
    }
    
    criterias = [
        {
            "bedrooms": 1,
            "max_price": 1600,
        },
    ]

    for area, location in places.items():
        new_listings: list[Listing] = []

        for criteria in criterias:
            min_bedrooms = criteria["bedrooms"]
            max_price = criteria["max_price"]
            index = 0
            all_listings_discovered = False
            print(f'searching for {min_bedrooms} beds in {area} under {max_price}...')
            while not all_listings_discovered:
                url = rightmove_url_builder(location=location, minimum_bedrooms=min_bedrooms, max_price=max_price, dontShow=["retirement", "student", "houseShare"], index=index)
                found_listings, found_listings_count = find_new_listings(url, id_is_in_database)
                index += found_listings_count
                all_listings_discovered = found_listings_count < RIGHTMOVE_FULL_PAGE_LENGTH
                new_listings.extend(found_listings)
                rest_time = 4.0 * random.random()
                time.sleep(rest_time)
            print(f'found {index} listings')

        print(f"found {len(new_listings)} new properties in {area}")

        for listing in new_listings[::-1]:
            #   TODO: find out why this might evaluate true
            #   if statement written after encountering exception
            #   has never been triggered since, but leaving it for protection
            if (id_is_in_database(listing.id)): 
                #print("Listing already found", listing.id)
                continue
            cursor.execute(*listing.insert_statement())
            email_subject = f"{listing.listing_title}, {listing.street_address} - £{listing.price}"
            send_email(creds=creds, to=to, sender=sender, subject=email_subject, body=listing.create_email_body())
            time.sleep(5 * random.random())
            connection.commit()
    
    time.sleep(10)

    return 0

if __name__ == "__main__":
    main()