from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Это решает проблему CORS для вашего плеера!

# Это адрес нашего нового, мощного API
# (Вы можете оставить его как есть, он публичный и стабильный)
MUZO_API_URL = "https://muzo-backend.vercel.app/api"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400

    # Формируем запрос к Muzo-backend
    search_url = f"{MUZO_API_URL}/search?q={query}&filter=songs&limit=10"
    try:
        # Делаем запрос к API
        response = requests.get(search_url)
        data = response.json()

        if data and data.get('success') and data.get('results'):
            # API вернул список треков. Мы просто возвращаем его вашему плееру.
            return jsonify(data['results'])
        else:
            return jsonify([])
    except Exception as e:
        # Логируем ошибку на сервере (поможет при отладке)
        print(f"Error: {e}")
        return jsonify({'error': f'search failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
