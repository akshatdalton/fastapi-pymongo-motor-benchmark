from locust import FastHttpUser, task


class TestGetSyncPymongo(FastHttpUser):
    @task
    def test_get_sync_pymongo(self):
        self.client.get("/sync/pymongo")
