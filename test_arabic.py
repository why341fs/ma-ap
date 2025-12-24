import requests
import json

url = "http://localhost:11434/api/generate"

data = {
    "model": "qwen-custom",
    "prompt": "اكتب لي تحية باللغة العربية",
    "stream": False
}

response = requests.post(url, json=data)
result = response.json()
print(result['response'])
