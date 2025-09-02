import psycopg2
import os
from tqdm import tqdm
import io

conn = psycopg2.connect(
    dbname=os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT")
)
cur = conn.cursor()

cur.execute('TRUNCATE TABLE "Cards" RESTART IDENTITY CASCADE')
cur.execute('TRUNCATE TABLE logs RESTART IDENTITY CASCADE')

def add_default_card(card_number, balance):
    cur.execute(
        'INSERT INTO "Cards" (card_number, balance) VALUES (%s, %s)',
        (card_number, balance)
    )
add_default_card("0000000000000000", 1000)
add_default_card("1111111111111111", 1000)

total_cards = 100_000_000

buffer = io.StringIO()
for i in tqdm(range(2, total_cards + 2), desc="Generating cards", unit="card"):
    card_number = f"{i:016d}"
    balance = 1000
    buffer.write(f"{card_number}\t{balance}\n")

buffer.seek(0)
cur.copy_from(buffer, 'Cards', columns=('card_number', 'balance'), sep='\t')

conn.commit()

cur.close()
conn.close()