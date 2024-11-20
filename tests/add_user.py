from uuid import uuid4
import requests

user_id = uuid4().hex
user_group = uuid4().hex

url = "http://127.0.0.1:8000/users/add"
data = {
    "user_id": user_id,
    "user_group": user_group,
    "username": "test_username",
    "email": "test@test.com",
    "password_hash": "test_hashed_password",
    "metadata": {"role": "admin", "created_at": "2024-10-01T00:00:00Z"},
}

response = requests.post(url, json=data)
print(response.status_code)
print(response.json())

print(f"User has been created with id = {user_id} and user_group = {user_group}")
