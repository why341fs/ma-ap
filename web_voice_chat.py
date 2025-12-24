from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('voice_chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    # Call Ollama API
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': 'gemma-arabic',
        'prompt': user_message,
        'stream': False
    })
    
    result = response.json()
    return jsonify({'response': result['response']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
