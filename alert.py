import requests
from bs4 import BeautifulSoup
import smtplib
import time
from email.mime.text import MIMEText

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

places = {}
RENT_BASE_URL = "https://www.rightmove.co.uk/property-to-rent/find.html"
EAST_LONDON = "USERDEFINEDAREA%5E%7B%22id%22%3A%228028516%22%7D"
SOUTH_LONDON = "USERDEFINEDAREA%5E%7B%22id%22%3A%228028525%22%7D"
locations = [SOUTH_LONDON, EAST_LONDON]

def right_move_url_builder(location: str, minimum_bedrooms: int, max_price: int, dontShow: list[str]=[], radius: float = 0.0):
    return f"{RENT_BASE_URL}?locationIdentifier={location}&radius={radius}&minBedrooms={minimum_bedrooms}&maxPrice={max_price}&dontShow={'%2C'.join(dontShow)}"

def find(req,first):
    try:
        print(req)
        r = requests.get(req)
        soup = BeautifulSoup(r.text, 'html.parser')

        props = soup.find_all("div", {"class": "propertyCard-section"})

        for i in props:
            spans = i.find('span')
            for a in i.find_all("a", {"class": "propertyCard-link"}, href=True):
                if(len(spans.text)>0):
                    if('https://www.rightmove.co.uk' + a['href'] not in places):
                        places['https://www.rightmove.co.uk' + a['href']] = spans.text
                        print(spans.text)
                        if(not first):
                                send_email(places['https://www.rightmove.co.uk' + a['href']] + "\n\n" + 'https://www.rightmove.co.uk' + a['href'])
    except Exception as ex:
        print("cannot connect", ex)
        time.sleep(5)

for i in range(10):
    for location in locations:
        url = right_move_url_builder(location=location, minimum_bedrooms=2, max_price=2500, dontShow=["retirement", "student", "houseShare"])
        find(req=url, first=True)
        time.sleep(2)

while True:
    for location in locations:
        url = right_move_url_builder(location=location, minimum_bedrooms=2, max_price=2500, dontShow=["retirement", "student", "houseShare"])
        find(req=url, first=False)
        time.sleep(2)
    time.sleep(60)