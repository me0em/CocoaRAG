from uuid import uuid4
import requests

conversation_id = "ae81f9b9002a453c8863a701a0c12769"

print(f"Choosed conversation: {conversation_id}")

user_id = "f0e8d7fc-c9e3-442f-8f53-973c20b3729f"
user_group = "acd4e4dd-5a62-46a0-aa93-f55365978384"
trace_id = uuid4().hex

# raw_query = "Describe point by point what the raven was doing in the house"
# raw_query = "Calc 5 + 4"
raw_query = "What means nevermore and who said this word?"

payload = {
    "user_id": user_id,
    "user_group": user_group,
    "conversation_id": conversation_id,
    "query": {"trace_id": trace_id, "content": raw_query},
}

url = "http://127.0.0.1:8000/query"

response = requests.post(url, json=payload)

print(f"Status Code: {response.status_code}")
print("Answer:")
print(response.json()["content"])
