from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io
import re

app = Flask(__name__)
CORS(app)

JIO_SAVAN_API = "https://www.jiosaavn.com/api.php"

def get_mp3_url(song_id):
    """Получает прямую ссылку на MP3 по ID трека"""
    params = {
        '__call': 'song.getDetails',
        'ctx': 'wap6',
        'pids': song_id,
        '_format': 'json',
        '_marker': '0',
        'api_version': '4',
    }
    
    try:
        response = requests.get(JIO_SAVAN_API, params=params, timeout=15)
        data = response.json()
        
        if data and song_id in data:
            song = data[song_id]
            encrypted_url = song.get('more_info', {}).get('encrypted_media_url')
            
            if encrypted_url:
                # JioSaavn иногда возвращает ссылку, иногда зашифрованный ID
                # Если это не URL, пробуем получить через другой эндпоинт
                if not encrypted_url.startswith('http'):
                    # Пробуем альтернативный способ
                    alt_params = {
                        '__call': 'song.getDetails',
                        'ctx': 'wap6',
                        'pids': song_id,
                        '_format': 'json',
                        '_marker': '0',
                        'api_version': '4',
                    }
                    alt_response = requests.get("https://c.saavncdn.com/api/songs", params={'pids': song_id})
                    alt_data = alt_response.json()
                    if alt_data and song_id in alt_data:
                        return alt_data[song_id].get('media_url')
                
                return encrypted_url
        return None
    except Exception as e:
        print(f"Error getting MP3 URL: {e}")
        return None

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    params = {
        '__call': 'autocomplete.get',
        'ctx': 'wap6',
        'query': query,
        '_format': 'json',
        '_marker': '0',
        'api_version': '4',
    }
    
    try:
        response = requests.get(JIO_SAVAN_API, params=params, timeout=15)
        data = response.json()
        
        results = []
        if 'songs' in data and data['songs']['data']:
            for song in data['songs']['data']:
                song_id = song.get('id')
                results.append({
                    'id': song_id,
                    'title': song.get('title'),
                    'artist': song.get('more_info', {}).get('primary_artists'),
                    'album': song.get('more_info', {}).get('album'),
                    'duration': song.get('more_info', {}).get('duration'),
                    'thumbnail': song.get('image'),
                    'url': f"https://music-bot.onrender.com/download?id={song_id}"
                })
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    song_id = request.args.get('id')
    if not song_id:
        return jsonify({'error': 'no id'}), 400
    
    try:
        mp3_url = get_mp3_url(song_id)
        
        if mp3_url and mp3_url.startswith('http'):
            audio_response = requests.get(mp3_url, timeout=30)
            return send_file(
                io.BytesIO(audio_response.content),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"track_{song_id}.mp3"
            )
        else:
            return jsonify({'error': 'could not get MP3 URL'}), 500
    
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
