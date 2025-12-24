from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('chat.html')

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

if __name__ == '__main__':
    print("💬 Starting text chat with Gemma...")
    print("📱 Open: http://localhost:5001")
    app.run(debug=True, port=5001)
