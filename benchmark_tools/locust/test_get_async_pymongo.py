from locust import FastHttpUser, task


class TestGetAsyncPymongo(FastHttpUser):
    @task
    def test_get_async_pymongo(self):
        self.client.get("/async/pymongo")
