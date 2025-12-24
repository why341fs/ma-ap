FROM python:3.12-slim

# Install curl and other dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api_server.py .

# Download model on first run (will be cached in persistent disk)
RUN ollama serve & sleep 5 && ollama pull gemma:2b && killall ollama || true

EXPOSE 5001

# Start script
COPY start.sh .
RUN chmod +x start.sh
CMD ["./start.sh"]
