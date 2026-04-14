from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    # Тот же API, что использует SoundBound
    params = {
        '__call': 'autocomplete.get',
        'ctx': 'wap6',
        'query': query,
        '_format': 'json',
        '_marker': '0',
        'api_version': '4',
    }
    
    try:
        response = requests.get("https://www.jiosaavn.com/api.php", params=params, timeout=15)
        data = response.json()
        
        results = []
        if 'songs' in data and data['songs']['data']:
            for song in data['songs']['data']:
                results.append({
                    'id': song.get('id'),
                    'title': song.get('title'),
                    'artist': song.get('more_info', {}).get('primary_artists'),
                    'duration': song.get('more_info', {}).get('duration'),
                    'thumbnail': song.get('image'),
                    'url': f"/download?id={song.get('id')}"
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download():
    song_id = request.args.get('id')
    if not song_id:
        return jsonify({'error': 'no id'}), 400
    
    # Пробуем несколько способов получить MP3 (как в SoundBound)
    mp3_url = None
    
    # Способ 1: прямой запрос к JioSaavn API
    params = {
        '__call': 'song.getDetails',
        'pids': song_id,
        'ctx': 'wap6',
        '_format': 'json',
        'api_version': '4',
    }
    
    try:
        response = requests.get("https://www.jiosaavn.com/api.php", params=params, timeout=15)
        data = response.json()
        
        if data and song_id in data:
            more_info = data[song_id].get('more_info', {})
            mp3_url = more_info.get('media_preview_url')
            if not mp3_url:
                mp3_url = more_info.get('encrypted_media_url')
    except:
        pass
    
    # Способ 2: через альтернативный API
    if not mp3_url or not mp3_url.startswith('http'):
        try:
            alt_response = requests.get("https://c.saavncdn.com/api/songs", params={'pids': song_id}, timeout=10)
            alt_data = alt_response.json()
            if alt_data and song_id in alt_data:
                mp3_url = alt_data[song_id].get('media_url')
        except:
            pass
    
    # Способ 3: через публичный прокси (запасной)
    if not mp3_url or not mp3_url.startswith('http'):
        try:
            proxy_response = requests.get(f"https://jiosaavn-proxy.vercel.app/api/song/{song_id}", timeout=10)
            proxy_data = proxy_response.json()
            mp3_url = proxy_data.get('url') or proxy_data.get('media_url')
        except:
            pass
    
    if mp3_url and mp3_url.startswith('http'):
        try:
            audio_response = requests.get(mp3_url, timeout=30)
            return send_file(
                io.BytesIO(audio_response.content),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"{song_id}.mp3"
            )
        except Exception as e:
            return jsonify({'error': f'download failed: {str(e)}'}), 500
    
    return jsonify({'error': 'no mp3 url'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
