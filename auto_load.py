import psycopg2
from dotenv import load_dotenv, dotenv_values
import os
import random

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)
cur = conn.cursor()

cur.execute('DELETE FROM "Cards"')

card_numbers = set()

def add_default_card(card_number, balance):
    card_numbers.add(card_number)
    cur.execute(
        'INSERT INTO "Cards" (card_number, balance) VALUES (%s, %s)',
        (card_number, balance)
    )
add_default_card("0000000000000000", 1000)
add_default_card("1111111111111111", 1000)

for i in range(10000000):
    card_number = ''.join(random.choices('0123456789', k=16))
    card_numbers.add(card_number)
    
    cur.execute(
        'INSERT INTO "Cards" (card_number, balance) VALUES (%s, %s)',
        (card_number, random.randint(0, 10000))
    )

conn.commit()

cur.close()
conn.close()