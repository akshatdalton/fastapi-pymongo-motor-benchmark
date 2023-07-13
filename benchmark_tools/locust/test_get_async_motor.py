from locust import FastHttpUser, task


class TestGetAsyncMotor(FastHttpUser):
    @task
    def test_get_async_motor(self):
        self.client.get("/async/motor")
