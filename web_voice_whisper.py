from flask import Flask, render_template, request, jsonify
import requests
import base64
import tempfile
import os
import whisper

app = Flask(__name__)

# Load Whisper model
print("Loading Whisper tiny model...")
stt_model = whisper.load_model("tiny")

@app.route('/')
def index():
    return render_template('voice_whisper.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        audio_data = data.get('audio')
        
        if not audio_data:
            return jsonify({'error': 'No audio data'}), 400
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data.split(',')[1])
        
        # Save to temp file
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_audio.write(audio_bytes)
        temp_audio.close()
        
        # Transcribe with Whisper
        result = stt_model.transcribe(temp_audio.name)
        user_text = result["text"]
        
        # Clean up
        os.unlink(temp_audio.name)
        
        # Send to Ollama
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma-arabic",
                "prompt": user_text,
                "stream": False
            }
        )
        
        ai_text = response.json()["response"]
        
        return jsonify({
            'user_text': user_text,
            'ai_text': ai_text
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 WEB VOICE CHAT WITH GEMMA (Whisper Tiny)")
    print("="*60)
    print("\n✨ Open your browser to: http://localhost:5001")
    print("📝 Using: Whisper tiny + Gemma via Ollama")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
