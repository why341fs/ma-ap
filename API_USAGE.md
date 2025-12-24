# Ollama API Endpoints

Base URL: `http://localhost:11434`

## Available Endpoints:

### 1. Generate Response
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma-arabic",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

### 2. Chat (with conversation history)
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma-arabic",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}'
```

### 3. List Models
```bash
curl http://localhost:11434/api/tags
```

### 4. Pull Model
```bash
curl http://localhost:11434/api/pull -d '{
  "name": "llama3.2:1b"
}'
```

### 5. Delete Model
```bash
curl http://localhost:11434/api/delete -d '{
  "name": "model-name"
}'
```

## Deploy to Network:

By default, Ollama only listens on localhost. To allow external access:

**Set environment variable:**
```bash
set OLLAMA_HOST=0.0.0.0:11434
```

Then restart Ollama service.

## Run Examples:

**Python:**
```bash
pip install requests
python ollama_api_example.py
```

**JavaScript:**
```bash
npm install axios
node ollama_api_example.js
```
