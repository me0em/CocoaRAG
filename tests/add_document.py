import json
import requests
from uuid import uuid4

user_id = "e0c659a922724cb8acedec7823a2fbd0"
user_group = "248f006d18b64993a1fba9fa7d6ef1cb"

trace_id = uuid4().hex
document_id = uuid4().hex

filename = r"Edgar Allan Poe - The Revan.txt"
files_dir_path = "../data"

metadata = {
    "filename": filename,
    "document_id": document_id,
    "user_id": user_id,
    "topic": "test",
    "location": "Boston"
}

with open(f"{files_dir_path}/{filename}", "r") as file:
    content: bytes = file.read().encode("utf-8")

files = {
    "file": (filename, content, "text/plain")
}

# data = json.dumps(metadata)

params = {
    "user_id": user_id,
    "user_group": user_group,
    "metadata": json.dumps(metadata)
}

url = "http://127.0.0.1:8000/documents/add/"

print("Ready to send the file")

response = requests.post(
    url,
    params=params,
    files=files
)

print(response.status_code)
print(response.json())
