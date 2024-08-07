import requests


message_thread = [
    {"role": "user", "content": "Hello World from user"},
    {"role": "assistant", "content": "Hello World from assistant"}
]


url = "https://chat.whitedune-3fe30ea7.eastus.azurecontainerapps.io/chat"
# url = "http://localhost:8000/chat"
response = requests.post(url, json=message_thread)
print(response.json())