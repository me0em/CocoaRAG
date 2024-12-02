from uuid import uuid4
import requests

conversation_id = "ae81f9b9002a453c8863a701a0c12769"

print(f"Choosed conversation: {conversation_id}")

user_id = "e0c659a922724cb8acedec7823a2fbd0"
user_group = "248f006d-18b6-4993-a1fb-a9fa7d6ef1cb"
trace_id = uuid4().hex

# raw_query = "Describe point by point what the raven was doing in the house"
# raw_query = "Calc 5 + 4"
# raw_query = "What means nevermore and who said this word?"
# raw_query = "Who is raven in his true nature?"
raw_query = "Who is Lenore?"

payload = {
    "user_id": user_id,
    "user_group": user_group,
    "conversation_id": conversation_id,
    "query": {
        "trace_id": trace_id,
        "content": raw_query
    }
}

url = "http://127.0.0.1:8000/query"

response = requests.post(
    url,
    json=payload
)

print(f"Status Code: {response.status_code}")
print("Answer:")
print(response.json()["content"])
