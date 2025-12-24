from flask import Flask, render_template, request, jsonify, send_file
import requests
import json
import os
import base64
from google.cloud import texttospeech

app = Flask(__name__)

# Set Google Cloud API key
os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'] = json.dumps({
    "type": "service_account",
    "project_id": "text-to-speech",
    "private_key_id": "dummy",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC=\n-----END PRIVATE KEY-----\n",
    "client_email": "dummy@text-to-speech.iam.gserviceaccount.com",
    "client_id": "dummy",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
})

# Initialize Google Cloud TTS client
GOOGLE_API_KEY = "AIzaSyA8MjLXjLZcm8jeiKr6VbiPrFbNGSaTzLU"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Call Ollama API
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': 'gemma-arabic',
            'prompt': user_message,
            'stream': False
        })
        
        result = response.json()
        bot_response = result.get('response', 'Sorry, I could not process that.')
        
        return jsonify({'response': bot_response})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.json
        text = data.get('text', '')
        language = data.get('language', 'en-US')
        
        # Use Google Cloud TTS REST API with API key
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}"
        
        payload = {
            "input": {"text": text},
            "voice": {
                "languageCode": language,
                "name": f"{language}-Standard-A"
            },
            "audioConfig": {
                "audioEncoding": "MP3",
                "speakingRate": 1.0,
                "pitch": 0.0
            }
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        audio_content = response.json()['audioContent']
        
        return jsonify({'audio': audio_content})
    
    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Starting web chat with Gemma...")
    print("📱 Open: http://localhost:5001")
    app.run(debug=True, port=5001)
