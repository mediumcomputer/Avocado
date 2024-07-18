import anthropic

client = anthropic.Anthropic(api_key="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")

message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)

print(message.content)

import requests
import os

api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjY5ZGJmZjE3LTYzYTEtNDc2ZS04NzIwLTI0ZTc3Y2MzYTZmMSIsImlhdCI6MTcyMDg0NTQwOSwic3ViIjoiZGV2ZWxvcGVyLzA3MTk0ODRkLTJjNzYtMDE3NC1lZWMwLTU5OWZkOWQyNDVhNSIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI1NC4yMTUuNjAuMTkxIiwiNjcuMTg4LjExMy4yMDciLCIyMy45My40OS4xMDEiXSwidHlwZSI6ImNsaWVudCJ9XX0.u2bpwpwJ0chDsoTJ3mPPjq7CNiue1G-QTHF4YdxB1E0na8w7ZPZ8rqKjofwWqoRma9AYb0ZzqQN2LhNK-vAqYg'

player_tag = 'PPUQL8YC'  # Replace with the player tag you're testing

url = f'https://api.clashroyale.com/v1/players/%23PPUQL8YC'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Content: {response.text}")