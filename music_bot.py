from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Это решает твою проблему с CORS!

# Прямой URL к API, который всегда работает
API_URL = "https://saavn.dev/api"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    # Делаем запрос к API Saavn
    search_url = f"{API_URL}/search/songs?query={query}&limit=10"
    try:
        response = requests.get(search_url)
        data = response.json()
        
        # API Saavn возвращает данные в поле 'data'
        if data and data.get('data', {}).get('results'):
            # Просто возвращаем данные как есть
            return jsonify({
                'code': 200,
                'data': {
                    'list': data['data']['results']
                }
            })
        else:
            return jsonify({'error': 'no results', 'data': {'list': []}}), 404
    except Exception as e:
        print(f"Error: {e}")  # Логируем ошибку на сервере
        return jsonify({'error': f'search failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
