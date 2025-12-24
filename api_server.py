from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for Gemma
    
    Request JSON:
    {
        "message": "Your question here",
        "model": "gemma-arabic"  // optional, defaults to gemma-arabic
    }
    
    Response JSON:
    {
        "response": "Bot response here",
        "status": "success"
    }
    """
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing "message" field',
                'status': 'error'
            }), 400
        
        user_message = data['message']
        model = data.get('model', 'gemma-arabic')
        
        # Call Ollama API
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': model,
            'prompt': user_message,
            'stream': False
        }, timeout=60)
        
        response.raise_for_status()
        result = response.json()
        bot_response = result.get('response', '')
        
        return jsonify({
            'response': bot_response,
            'status': 'success',
            'model': model
        })
    
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout',
            'status': 'error'
        }), 504
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': f'Ollama API error: {str(e)}',
            'status': 'error'
        }), 502
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check if Ollama is running
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        response.raise_for_status()
        
        return jsonify({
            'status': 'healthy',
            'ollama': 'running'
        })
    except:
        return jsonify({
            'status': 'unhealthy',
            'ollama': 'not running'
        }), 503

@app.route('/api/models', methods=['GET'])
def models():
    """List available models"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        response.raise_for_status()
        
        models_data = response.json()
        model_names = [model['name'] for model in models_data.get('models', [])]
        
        return jsonify({
            'models': model_names,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    print("🚀 Gemma API Server Starting...")
    print("📡 API Endpoint: http://localhost:5001/api/chat")
    print("💚 Health Check: http://localhost:5001/api/health")
    print("📋 List Models: http://localhost:5001/api/models")
    print("\n📝 Example usage:")
    print('curl -X POST http://localhost:5001/api/chat \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"message": "Hello, how are you?"}\'')
    print()
    app.run(host='0.0.0.0', port=5001, debug=False)
