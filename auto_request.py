# locustfile.py
from locust import HttpUser, task, between
from dotenv import load_dotenv
import psycopg2
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

cur.execute('SELECT card_number FROM "Cards"')
card_numbers = list(cur.fetchall())
print(len(card_numbers))

class TestUser(HttpUser):
    wait_time = between(0.2, 0.4)

    @task
    def default_transaction(self):
        self.client.post("/transaction", json={
            "src_card": "0000000000000000",
            "dest_card": "1111111111111111",
            "amount": 10
        })
        self.client.post("/transaction", json={
            "src_card": "1111111111111111",
            "dest_card": "0000000000000000",
            "amount": 10
        })

    @task
    def random_transaction(self):
        card1, card2 = random.sample(card_numbers, k=2)
        self.client.post("/transaction", json={
            "src_card": card1,
            "dest_card": card2,
            "amount": 10
        })
