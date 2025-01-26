import sys
import psycopg
import os
from dotenv import load_dotenv


load_dotenv()

database = os.getenv("DATABASE_NAME")
user = os.getenv("DATABASE_USERNAME")
password = os.getenv("DATABASE_PASSWORD")
port = os.getenv("DATABASE_PORT")
host = os.getenv("DATABASE_HOST")

if not database or not user or not password or not host or not port:
    print("Database options not filled")
    sys.exit(-1)

cursor = None
connection = None


def get_db_connection():
    global connection
    if connection == None:
        connection = psycopg.connect(
            user=user, password=password, database=database, host=host
        )

    return connection


def get_db_client():
    global cursor
    if cursor == None:
        connection = get_db_connection()
        cursor = connection.cursor()

    return cursor
