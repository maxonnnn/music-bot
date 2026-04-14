from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Стабильный публичный API, который работает через Cloudflare
PROXY_API = "https://api.saavn.me"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    # Формируем запрос к API
    search_url = f"{PROXY_API}/search/songs?query={query}&limit=10"
    
    try:
        response = requests.get(search_url, timeout=10)
        data = response.json()
        
        if data and data.get('data', {}).get('results'):
            # Возвращаем данные в нужном формате
            return jsonify({
                'code': 200,
                'data': {
                    'list': data['data']['results']
                }
            })
        else:
            return jsonify({'error': 'no results', 'data': {'list': []}}), 404
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'request timeout'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': f'search failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
