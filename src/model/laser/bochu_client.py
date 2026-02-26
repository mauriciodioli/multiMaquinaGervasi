# bochu_client.py
import requests

class BochuClient:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def completed_tasks(self, machine_id, start, end):
        url = f"{self.base_url}/api/production/queryCompletedTaskList"
        payload = {
            "machineToolId": machine_id,
            "startTime": start,
            "endTime": end
        }
        r = requests.post(url, json=payload, headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json()
