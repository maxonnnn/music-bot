from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Это решает твою проблему с CORS!

# Адрес нового, более стабильного API
JIO_SAVAN_API = "https://www.jiosaavn.com/api.php"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    # Параметры запроса для JioSaavn
    params = {
        '__call': 'autocomplete.get',
        'ctx': 'wap6',
        'query': query,
        '_format': 'json',
        '_marker': '0',
        'api_version': '4',
    }
    
    try:
        response = requests.get(JIO_SAVAN_API, params=params)
        data = response.json()
        
        # Преобразуем ответ JioSaavn в привычный формат
        formatted_results = []
        if 'songs' in data and data['songs']['data']:
            for song in data['songs']['data']:
                formatted_results.append({
                    'id': song['id'],
                    'name': song['title'],
                    'singer': song['more_info']['primary_artists'],
                    'time': song['more_info']['duration'],
                    'pic': song['image'],
                    'code': 200,
                    'data': {
                        'url': f"https://www.jiosaavn.com/song/{song['id']}"
                    }
                })
        
        return jsonify({
            'code': 200,
            'data': {
                'list': formatted_results
            }
        })
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/info')
def info():
    track_id = request.args.get('id')
    if not track_id:
        return jsonify({'error': 'no id'}), 400
    
    # Параметры запроса для получения ссылки на MP3
    params = {
        '__call': 'song.getDetails',
        'ctx': 'wap6',
        'pids': track_id,
        '_format': 'json',
        '_marker': '0',
        'api_version': '4',
    }
    
    try:
        response = requests.get(JIO_SAVAN_API, params=params)
        data = response.json()
        
        if data and data.get(track_id):
            song = data[track_id]
            return jsonify({
                'code': 200,
                'data': {
                    'url': song['more_info']['encrypted_media_url']
                }
            })
        else:
            return jsonify({'error': 'info not found'}), 404
    except Exception as e:
        return jsonify({'error': f'info failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
