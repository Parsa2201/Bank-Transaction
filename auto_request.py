# locustfile.py
from locust import HttpUser, task, between

class TestUser(HttpUser):
    wait_time = between(0.1, 0.4)

    @task
    def transaction(self):
        self.client.post("/transaction", json={
            "src_card": "0007060629109952",
            "dest_card": "0026097768678012",
            "amount": 10
        })
        self.client.post("/transaction", json={
            "src_card": "0026097768678012",
            "dest_card": "0007060629109952",
            "amount": 10
        })