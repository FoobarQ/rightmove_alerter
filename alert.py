import requests
from bs4 import BeautifulSoup
import smtplib
import time
from email.mime.text import MIMEText
import random

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

places = {
    "South London": SOUTH_LONDON,
    "East London": EAST_LONDON
}

def right_move_url_builder(location: str, minimum_bedrooms: int, max_price: int, dontShow: list[str]=[], radius: float = 0.0, index: int = 0):
    return f"{RENT_URL}?locationIdentifier={location}&radius={radius}&minBedrooms={minimum_bedrooms}&maxPrice={max_price}&index={index}&dontShow={'%2C'.join(dontShow)}&furnishTypes=&keywords="

def find(search_url: str):
    search_response = requests.get(search_url)
    found_all_properties = not search_response.ok
    if found_all_properties:
        raise Exception("No more properties!")
    
    soup = BeautifulSoup(search_response.text, 'html.parser')
    html = soup.find_all("div", {"class": "propertyCard-wrapper"})

    property_count = len(html)
    found_all_properties = property_count == 0
    if (found_all_properties):    
        raise Exception("No more properties!")

    for element in html[1:]:    #   skip the promoted ad at the top
        description_element = element.find("div", {"class": "propertyCard-description"})
        relative_url: str = description_element.find("a").get('href')
        ad_url = f"{BASE_URL}{relative_url}"
        url_parts = relative_url.replace("#", "").split("/")
        found_all_properties = len(url_parts) < 2

        if (found_all_properties):
            raise Exception("No more properties!")

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
        
        #   TODO: replaced with a database update
        #   if not in database, CREATE
        #   else throw raise("everything updated")
        print("")
        print(f"id: {id}")
        print(f"title: {title}")
        print(f"street address: {street_address}")
        print(f"country: {country_code}")
        print(f"price: {price}")
        print(f"description: {description}")
        print(f"url: {ad_url}")
        print("")

    return property_count

for area, location in places.items():
    index = 0
    page_number = 1
    try:
        while True:
            print(f"page {page_number}")
            page_number += 1
            url = right_move_url_builder(location=location, minimum_bedrooms=2, max_price=2500, dontShow=["retirement", "student", "houseShare"], index=index)
            index += find(url)

            rest_time = 4.0 * random.random()
            print(f"sleeping for {rest_time} seconds")
            time.sleep(rest_time)
            
    except Exception as no_more_properties_error:
        print(no_more_properties_error)
        print(f"found {index} properties in {area}")