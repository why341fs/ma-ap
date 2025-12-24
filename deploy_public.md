# Deploy Ollama to Public Internet with HTTPS

## Option 1: Ngrok (Quick & Easy - For Testing)

1. Download ngrok: https://ngrok.com/download
2. Run Ollama (already running on localhost:11434)
3. Run ngrok:
```bash
ngrok http 11434
```
4. You'll get a public HTTPS URL like: `https://abc123.ngrok.io`

**Use in your app:**
```javascript
const API_URL = 'https://abc123.ngrok.io';
```

**Pros:** Instant HTTPS, no configuration
**Cons:** Free tier has random URLs, limited requests

---

## Option 2: Cloudflare Tunnel (Free & Permanent)

1. Install Cloudflare Tunnel:
```bash
winget install Cloudflare.cloudflared
```

2. Authenticate:
```bash
cloudflared tunnel login
```

3. Create tunnel:
```bash
cloudflared tunnel create ollama
```

4. Configure tunnel (create config.yml):
```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: C:\Users\YOUR_USER\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: ollama.yourdomain.com
    service: http://localhost:11434
  - service: http_status:404
```

5. Route DNS:
```bash
cloudflared tunnel route dns ollama ollama.yourdomain.com
```

6. Run tunnel:
```bash
cloudflared tunnel run ollama
```

**Pros:** Free, permanent domain, automatic HTTPS
**Cons:** Requires domain name

---

## Option 3: Deploy to Cloud with Reverse Proxy

### Using VPS (DigitalOcean, AWS, etc.)

1. Upload your model to cloud server
2. Install Nginx + Certbot for SSL
3. Configure Nginx reverse proxy:

```nginx
server {
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. Get SSL certificate:
```bash
certbot --nginx -d api.yourdomain.com
```

---

## Option 4: Deploy to Railway/Render

These platforms can host your Ollama instance with automatic HTTPS.

---

## Security Warning ⚠️

When exposing to public internet:
- Add authentication (API keys)
- Rate limiting
- Monitor usage
- Consider costs (bandwidth, compute)

---

## Example: Protected API with Flask

```python
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
API_KEY = os.getenv('API_KEY', 'your-secret-key')

@app.route('/api/chat', methods=['POST'])
def chat():
    # Check API key
    if request.headers.get('Authorization') != f'Bearer {API_KEY}':
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Forward to Ollama
    data = request.json
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'gemma-arabic',
        'prompt': data['prompt'],
        'stream': False
    })
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Then use ngrok/cloudflare on port 5000 with authentication.
