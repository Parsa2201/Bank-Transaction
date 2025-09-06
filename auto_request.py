from locust import HttpUser, task, between
import psycopg2
import os
import random
import time
from requests.exceptions import HTTPError

conn = psycopg2.connect(
    dbname=os.getenv("DATABASE_NAME"),
    user=os.getenv("DATABASE_USER"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT")
)
cur = conn.cursor()

cur.execute('SELECT card_number FROM cards LIMIT 100')
card_numbers = list(cur.fetchall())
print(len(card_numbers))

class TestUser(HttpUser):
    wait_time = between(0.1, 0.2)

    @task
    def default_transaction(self):
        for src, dest in [("0000000000000000", "1111111111111111"),
                          ("1111111111111111", "0000000000000000")]:
            with self.client.post(
                "/transaction",
                json={"src_card": src, "dest_card": dest, "amount": 10},
                catch_response=True
            ) as response:
                if response.status_code == 400:
                    response.success()  # treat 400 as success
                elif response.status_code != 200:
                    response.failure(f"Unexpected status code: {response.status_code}")

    @task
    def random_transaction(self):
        card1, card2 = random.sample(card_numbers, k=2)
        with self.client.post(
            "/transaction", 
            json={
                "src_card": card1[0],
                "dest_card": card2[0],
                "amount": 10},
            catch_response=True
        ) as response:
            if response.status_code == 400:
                response.success()  # treat 400 as success
            elif response.status_code != 200:
                response.failure(f"Unexpected status code: {response.status_code}")

