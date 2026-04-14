from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app)

# Публичный API JioSaavn
JIO_SAVAN_API = "https://www.jiosaavn.com/api.php"

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
                results.append({
                    'id': song.get('id'),
                    'title': song.get('title'),
                    'artist': song.get('more_info', {}).get('primary_artists'),
                    'album': song.get('more_info', {}).get('album'),
                    'duration': song.get('more_info', {}).get('duration'),
                    'thumbnail': song.get('image'),
                    'url': f"https://music-bot.onrender.com/download?id={song.get('id')}"
                })
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    song_id = request.args.get('id')
    if not song_id:
        return jsonify({'error': 'no id'}), 400
    
    # Получаем прямую ссылку на MP3
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
            mp3_url = song.get('more_info', {}).get('encrypted_media_url')
            
            if mp3_url:
                # Скачиваем MP3
                audio_response = requests.get(mp3_url, timeout=30)
                return send_file(
                    io.BytesIO(audio_response.content),
                    mimetype='audio/mpeg',
                    as_attachment=True,
                    download_name=f"{song.get('title', 'track')}.mp3"
                )
        
        return jsonify({'error': 'download failed'}), 500
    
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
