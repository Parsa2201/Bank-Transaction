from locust import HttpUser, task, between
import psycopg2
import os
import random
import time

conn = psycopg2.connect(
    dbname=os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT")
)
cur = conn.cursor()

cur.execute('SELECT card_number FROM "Cards"')
card_numbers = list(cur.fetchall())
print(len(card_numbers))

class TestUser(HttpUser):
    wait_time = between(0.1, 0.2)

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
            "src_card": card1[0],
            "dest_card": card2[0],
            "amount": 10
        })
