from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Разрешаем твоему плееру обращаться к этому серверу

API_BASE_URL = "https://musicapi.x007.workers.dev"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    # Параметр 'limit' просит API вернуть больше треков
    api_url = f"{API_BASE_URL}/search?q={query}&limit=10"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        # API возвращает список треков в поле 'response'
        if data and data.get('status') == 200:
            return jsonify(data.get('response', []))
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
