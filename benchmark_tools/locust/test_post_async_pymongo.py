import random

from locust import FastHttpUser, task


class TestPostAsyncPymongo(FastHttpUser):
    @task
    def test_post_async_pymongo(self):
        data = {"user_id": random.randint(100, 5000)}
        self.client.post("/async/pymongo", json=data)
