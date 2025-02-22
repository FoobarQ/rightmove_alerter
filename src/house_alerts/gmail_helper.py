import os
import base64
import time
import random

from src.dal.connection import get_db_connection
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.house_alerts.constants import SENDER
from src.house_alerts.listing import Listing

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
]


def get_gmail_credentials(scopes=SCOPES):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def send_email(creds, to: str, sender: str, subject: str, body: str):
    """From google docs"""

    try:
        service = build("gmail", "v1", credentials=creds)
        message = MIMEMultipart()

        message.attach(MIMEText(body, "html"))

        message["To"] = to
        message["From"] = sender
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}

        send_message = (
            service.users().messages().send(userId="me", body=create_message).execute()
        )

        print(f'Message Id: {send_message["id"]}, subject: {subject}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None

    return send_message


def send_emails(to: str, listings: list[Listing]):

    new_listings = listings[::-1]
    connection = get_db_connection()
    creds = get_gmail_credentials()

    if len(new_listings) < 8:
        for listing in new_listings:
            cursor = connection.cursor()
            cursor.execute(*listing.update_statement())
            cursor.close()
            connection.commit()
            email_subject = (
                f"{listing.listing_title}, {listing.street_address} - £{listing.price}"
            )
            send_email(
                creds=creds,
                to=to,
                sender=SENDER,
                subject=email_subject,
                body=listing.create_email_body(),
            )
            time.sleep(5 * random.random())

    for listing_chunk in [
        new_listings[x : x + 8] for x in range(0, len(new_listings), 8)
    ]:
        for y in listing_chunk:
            cursor = connection.cursor()
            cursor.execute(*y.update_statement())
            cursor.close()
            connection.commit()
        email_subject = f"{len(listing_chunk)} new rental properties found"
        email_body = f"""<html>
        <head>
            <style>
                .image {{
                    width: 50px;
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
                    {''.join([row.create_email_row() for row in listing_chunk])}
                </tbody>
            </table>
        </body>
    </html>"""
        send_email(
            creds=creds,
            to=to,
            sender=SENDER,
            subject=email_subject,
            body=email_body,
        )
        time.sleep(15 * random.random())
