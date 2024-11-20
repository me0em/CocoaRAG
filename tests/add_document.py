import json
import requests
from uuid import uuid4


user_id = "f0e8d7fc-c9e3-442f-8f53-973c20b3729f"
user_group = "acd4e4dd-5a62-46a0-aa93-f55365978384"

trace_id = uuid4().hex
document_id = uuid4().hex

filename = r"Edgar Allan Poe - The Revan.txt"
files_dir_path = "../data"

metadata = {
    "filename": filename,
    "document_id": document_id,
    "user_id": user_id,
    "topic": "test",
    "location": "Boston",
}

with open(f"{files_dir_path}/{filename}", "r") as file:
    content: bytes = file.read().encode("utf-8")

files = {"file": (filename, content, "text/plain")}

# data = json.dumps(metadata)

params = {
    "user_id": user_id,
    "user_group": user_group,
    "metadata": json.dumps(metadata),
}

url = "http://127.0.0.1:8000/documents/add/"


response = requests.post(url, params=params, files=files)

print(response.status_code)
print(response.json())
