import requests
from bs4 import BeautifulSoup
import smtplib
import time
from email.mime.text import MIMEText
from twilio.rest import Client 

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

def send_text(txt,number):
    account_sid = '<ACCOUNT_SID>' 
    auth_token = '<AUTH_TOKEN>' 
    client = Client(account_sid, auth_token) 
    
    message = client.messages.create(  
                                messaging_service_sid='<MESSAGING_SERVICE_SID>', 
                                body=txt,      
                                to=number
                            )


places = {}

searches = [
            "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E4001&minBedrooms=2&maxPrice=1750&radius=0.5&propertyTypes=&mustHave=&dontShohttps://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E7610&minBedrooms=2&maxPrice=1750&radius=0.5&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords=",# reading
            "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=BRANCH%5E102784&minBedrooms=2&propertyTypes=&includeLetAgreed=true&mustHave=&dontShow=&furnishTypes=&keywords=", #l and q
            "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E8873&minBedrooms=2&maxPrice=1750&radius=0.5&propertyTypes=&mustHave=&dontShoww=&furnishTypes=&keywords=", #Greenwich
            "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E8984&minBedrooms=2&maxPrice=1750&radius=0.5&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords=", #Sydenham
            "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=BRANCH%5E97670&minBedrooms=2&maxPrice=1750&propertyTypes=&includeLetAgreed=true&mustHave=&dontShow=&furnishTypes=&keywords=", #Folio
            "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E70328&minBedrooms=2&maxPrice=1750&propertyTypes=&mustHave=&dontShow=&furnishTypes=&keywords="
            ]

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
    for s in searches:
        find(s, True)
        time.sleep(2)

while True:
    for s in searches:
        find(s, False)
        time.sleep(2)
    time.sleep(60)