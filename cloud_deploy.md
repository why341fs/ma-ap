# Permanent Cloud Deployment Options for Ollama

## Option 1: DigitalOcean/Linode/Vultr VPS (Recommended)

**Cost:** $6-12/month for 4GB RAM VPS

### Steps:
1. Create droplet/VPS (Ubuntu 22.04)
2. SSH into server
3. Install Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

4. Pull your model:
```bash
ollama pull gemma:2b
ollama create gemma-arabic -f Modelfile-gemma
```

5. Install Nginx:
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

6. Configure Nginx (`/etc/nginx/sites-available/ollama`):
```nginx
server {
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

7. Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

8. Get free SSL certificate:
```bash
sudo certbot --nginx -d api.yourdomain.com
```

**Access:** `https://api.yourdomain.com`

---

## Option 2: AWS EC2

**Cost:** Free tier (1 year) or ~$10/month

1. Launch EC2 instance (t3.medium, 4GB RAM)
2. Open port 443 in Security Group
3. Follow same steps as Option 1
4. Use Elastic IP for permanent address

---

## Option 3: Oracle Cloud (FREE Forever)

**Cost:** $0 - Free tier includes 24GB RAM

1. Sign up: https://cloud.oracle.com/
2. Create Compute Instance (ARM or x86)
3. Choose "Always Free" eligible shape
4. Install Ollama and configure Nginx (same as Option 1)

**Best for budget:** Completely free, very generous specs

---

## Option 4: Hugging Face Spaces (Easiest)

**Cost:** Free or $0.60/hour for GPU

1. Create Space: https://huggingface.co/spaces
2. Create `app.py`:
```python
import gradio as gr
import subprocess
import requests
import os

# Install and start Ollama
subprocess.run(["curl", "-fsSL", "https://ollama.com/install.sh", "-o", "install.sh"])
subprocess.run(["sh", "install.sh"])
subprocess.Popen(["ollama", "serve"])
subprocess.run(["ollama", "pull", "gemma:2b"])

def chat(message, history):
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'gemma:2b',
        'prompt': message,
        'stream': False
    })
    return response.json()['response']

demo = gr.ChatInterface(chat)
demo.launch(server_name="0.0.0.0", server_port=7860)
```

3. Deploy - Automatic HTTPS URL!

---

## Option 5: Modal.com (Serverless, Pay Per Use)

**Cost:** Free tier, then ~$0.02/minute when running

```python
import modal

app = modal.App("ollama-api")

@app.function(
    image=modal.Image.debian_slim().run_commands(
        "curl -fsSL https://ollama.com/install.sh | sh",
        "ollama pull gemma:2b"
    ),
    gpu="any"
)
@modal.web_endpoint(method="POST")
def generate(data: dict):
    import subprocess
    import json
    
    result = subprocess.run(
        ["ollama", "run", "gemma:2b", data["prompt"]],
        capture_output=True,
        text=True
    )
    return {"response": result.stdout}
```

Deploy: `modal deploy app.py`
Access: Automatic HTTPS endpoint

---

## Recommended: Oracle Cloud (Free) or DigitalOcean ($6/mo)

### Quick Start Script for Ubuntu VPS:

```bash
#!/bin/bash
# Save as setup.sh and run on your VPS

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull gemma:2b

# Install Nginx
apt update
apt install -y nginx certbot python3-certbot-nginx

# Create Nginx config
cat > /etc/nginx/sites-available/ollama << 'EOF'
server {
    server_name YOUR_DOMAIN.com;
    
    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/ollama /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Get SSL (replace YOUR_DOMAIN and EMAIL)
certbot --nginx -d YOUR_DOMAIN.com --email YOUR_EMAIL --agree-tos -n

echo "Done! Access at https://YOUR_DOMAIN.com"
```

---

## Need a Domain?

Free options:
- Freenom (free .tk, .ml domains)
- freedns.afraid.org (free subdomains)
- DuckDNS (free dynamic DNS)

Or buy: Namecheap, Cloudflare ($1-10/year)
