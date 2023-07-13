import random

from locust import FastHttpUser, task


class TestPostSyncPymongo(FastHttpUser):
    @task
    def test_post_sync_pymongo(self):
        data = {"user_id": random.randint(100, 5000)}
        self.client.post("/sync/pymongo", json=data)
