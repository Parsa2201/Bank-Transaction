import psycopg2
from dotenv import load_dotenv
import os
import random
from tqdm import tqdm

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

total_cards = 10_000_000
batch_size=100_000

for i in tqdm(range(0, total_cards, batch_size), desc="Inserting cards", unit="card"):
    batch = []
    for j in range(batch_size):
        card_number = ''.join(random.choices('0123456789', k=16))
        if card_number not in card_numbers:
            batch.append((card_number, random.randint(0, 10000)))
        card_numbers.add(card_number)
    
    cur.executemany('INSERT INTO "Cards" (card_number, balance) VALUES (%s, %s)',batch)

conn.commit()

cur.close()
conn.close()