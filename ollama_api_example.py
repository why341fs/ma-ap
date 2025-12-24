import requests
import json

# Ollama API endpoint
BASE_URL = "http://localhost:11434"

# 1. Generate a response (non-streaming)
def chat(prompt, model="gemma-arabic"):
    url = f"{BASE_URL}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    return response.json()["response"]

# 2. Chat with conversation history
def chat_with_history(messages, model="gemma-arabic"):
    url = f"{BASE_URL}/api/chat"
    data = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    response = requests.post(url, json=data)
    return response.json()["message"]["content"]

# 3. Streaming response
def chat_stream(prompt, model="gemma-arabic"):
    url = f"{BASE_URL}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    response = requests.post(url, json=data, stream=True)
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if "response" in chunk:
                print(chunk["response"], end="", flush=True)
            if chunk.get("done"):
                print()
                break

# Example usage
if __name__ == "__main__":
    print("=== Simple Generation ===")
    result = chat("What is AI?")
    print(result)
    
    print("\n=== Chat with History ===")
    messages = [
        {"role": "user", "content": "Hello, what's your name?"},
    ]
    result = chat_with_history(messages)
    print(result)
    
    print("\n=== Streaming ===")
    chat_stream("Tell me a short story")
