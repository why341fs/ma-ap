# Deploy Gemma API - Keep it Online 24/7

## Option 1: Render.com (FREE - Best for Ollama)

**Why Render**: Free tier includes persistent disk, perfect for storing Ollama models!

### Step-by-Step:

1. **Create account**: https://render.com
2. **Push code to GitHub** (if not already)
3. **Create these files in your repo**:

**render.yaml** (Blueprint file):
```yaml
services:
  - type: web
    name: gemma-api
    env: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: PORT
        value: 5001
    disk:
      name: ollama-models
      mountPath: /root/.ollama
      sizeGB: 10
    plan: free
```

**Dockerfile**:
```dockerfile
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
```

**start.sh**:
```bash
#!/bin/bash
ollama serve &
sleep 5
python api_server.py
```

**requirements.txt**:
```
flask==3.1.2
flask-cors==6.0.2
requests==2.32.5
```

4. **Deploy**:
   - Go to Render Dashboard → "New" → "Blueprint"
   - Connect your GitHub repo
   - Render will automatically detect `render.yaml`
   - Click "Apply" → Wait ~5-10 minutes for build
   - Your API will be live at `https://gemma-api-xxxx.onrender.com`

5. **Test**:
```bash
curl https://your-app.onrender.com/api/health
```

**Notes**:
- ⚠️ Free tier sleeps after 15 min inactivity (takes ~30s to wake)
- ✅ Models persist between deploys (saved in disk)
- ✅ No credit card required
- ✅ Automatic HTTPS included

---

## Option 2: Railway.app (Alternative Free Tier)

1. **Create account**: https://railway.app
2. **Create Dockerfile**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy files
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY api_server.py .

# Download Gemma model
RUN ollama serve & sleep 5 && ollama pull gemma:2b

# Expose port
EXPOSE 5001

# Start both Ollama and API
CMD ollama serve & sleep 5 && python api_server.py
```

3. **Create requirements.txt**:
```
flask==3.1.2
flask-cors==6.0.2
requests==2.32.5
```

4. **Deploy**: Push to GitHub → Connect to Railway → Deploy

---

## Option 2: DigitalOcean/Vultr VPS ($6/month)

### Setup:
```bash
# SSH into server
ssh root@your-server-ip

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Install Python
apt update && apt install python3-pip

# Clone your code
cd /opt
git clone your-repo
cd your-repo

# Install dependencies
pip3 install flask flask-cors requests

# Pull model
ollama pull gemma:2b

# Create systemd service for Ollama
nano /etc/systemd/system/ollama.service
```

**ollama.service:**
```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/ollama serve
Restart=always

[Install]
WantedBy=multi-user.target
```

**Create API service:**
```bash
nano /etc/systemd/system/gemma-api.service
```

**gemma-api.service:**
```ini
[Unit]
Description=Gemma API Server
After=ollama.service
Requires=ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/your-repo
ExecStart=/usr/bin/python3 api_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start services:**
```bash
systemctl daemon-reload
systemctl enable ollama
systemctl enable gemma-api
systemctl start ollama
systemctl start gemma-api

# Check status
systemctl status ollama
systemctl status gemma-api
```

---

## Option 3: Local Windows (Keep Running)

### Using NSSM (Non-Sucking Service Manager):

1. **Download NSSM**: https://nssm.cc/download
2. **Install as Windows Service**:

```powershell
# Install Ollama as service (if not already)
# Ollama installer does this automatically

# Install API as service
nssm install GemmaAPI "C:\Users\YourUser\AppData\Local\Programs\Python\Python312\python.exe" "C:\localai\api_server.py"
nssm set GemmaAPI AppDirectory C:\localai
nssm set GemmaAPI DisplayName "Gemma API Server"
nssm set GemmaAPI Start SERVICE_AUTO_START

# Start service
nssm start GemmaAPI

# Check status
nssm status GemmaAPI
```

---

## Option 4: Docker (Universal)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"
    restart: always

  gemma-api:
    build: .
    ports:
      - "5001:5001"
    depends_on:
      - ollama
    restart: always
    environment:
      - OLLAMA_HOST=http://ollama:11434

volumes:
  ollama-data:
```

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY api_server.py .

EXPOSE 5001

CMD ["python", "api_server.py"]
```

**Run:**
```bash
docker-compose up -d
```

---

## Setup Nginx Reverse Proxy (For all options)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

**Get SSL certificate:**
```bash
certbot --nginx -d api.yourdomain.com
```

---

## Monitor & Auto-Restart

**For VPS - Add health check cron:**
```bash
crontab -e
```

Add:
```
*/5 * * * * systemctl is-active --quiet gemma-api || systemctl restart gemma-api
```

---

## My Recommendation:

- **Hobby/Testing**: Railway.app (free)
- **Production**: DigitalOcean VPS ($6/mo) with systemd
- **Local**: NSSM Windows Service

All options will keep your API running 24/7 with auto-restart on failure!
