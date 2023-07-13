import random

from locust import FastHttpUser, task


class TestPostAsyncMotor(FastHttpUser):
    @task
    def test_post_async_motor(self):
        data = {"user_id": random.randint(100, 5000)}
        self.client.post("/async/motor", json=data)
