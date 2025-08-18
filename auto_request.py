# locustfile.py
from locust import HttpUser, task, between

class TestUser(HttpUser):
    wait_time = between(0.1, 0.4)

    @task
    def transaction(self):
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