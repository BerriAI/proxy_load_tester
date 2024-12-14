import os
import uuid
from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(0.5, 1)

    @task
    def anthropic_completion(self):
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 256,
            "messages": [
                {"role": "user", "content": f"{uuid.uuid4()} Hello, world tell me 2 sentences"}
            ],
            "litellm_metadata": {"tags": ["hi"]}
        }
        
        headers = {
            'anthropic-version': '2023-06-01',
            'tags': "['hi']",
            'content-type': 'application/json',
            'Authorization': 'Bearer sk-1234'
        }
        
        response = self.client.post("anthropic/v1/messages", json=payload, headers=headers)
        if response.status_code != 200:
            with open("error.txt", "a") as error_log:
                error_log.write(response.text + "\n")
