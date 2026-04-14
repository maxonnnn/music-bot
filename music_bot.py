from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Это решает твою проблему с CORS!

# Это адрес API, который мы используем
GEQUHAI_API_URL = "https://www.gequhai.com/api"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    # Отправляем запрос на Gequhai API для поиска
    search_url = f"{GEQUHAI_API_URL}/music?search={query}"
    try:
        response = requests.get(search_url)
        data = response.json()
        
        if data and data.get('code') == 200:
            # Возвращаем результат прямо из API
            return jsonify(data)
        else:
            return jsonify({'error': 'no results', 'data': {'list': []}}), 404
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/info')
def info():
    track_id = request.args.get('id')
    if not track_id:
        return jsonify({'error': 'no id'}), 400
    
    # Отправляем запрос на Gequhai API для получения ссылки на MP3
    info_url = f"{GEQUHAI_API_URL}/music/info?id={track_id}"
    try:
        response = requests.get(info_url)
        data = response.json()
        
        if data and data.get('code') == 200:
            # Возвращаем результат прямо из API
            return jsonify(data)
        else:
            return jsonify({'error': 'info not found'}), 404
    except Exception as e:
        return jsonify({'error': f'info failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
