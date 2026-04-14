from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app)

# Альтернативный публичный API для JioSaavn
SAVAN_API = "https://saavn.me"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    try:
        response = requests.get(f"{SAVAN_API}/search/songs?query={query}&limit=10", timeout=15)
        data = response.json()
        
        results = []
        if 'data' in data and 'results' in data['data']:
            for song in data['data']['results']:
                # Получаем ссылку на MP3 (320kbps)
                download_url = None
                if 'downloadUrl' in song:
                    for quality in song['downloadUrl']:
                        if quality.get('quality') == '320kbps':
                            download_url = quality.get('link')
                            break
                    if not download_url and song['downloadUrl']:
                        download_url = song['downloadUrl'][0].get('link')
                
                results.append({
                    'id': song.get('id'),
                    'title': song.get('name'),
                    'artist': song.get('artists', {}).get('primary', [{}])[0].get('name') if song.get('artists') else 'Unknown',
                    'duration': song.get('duration'),
                    'thumbnail': song.get('image', [{}])[2].get('link') if song.get('image') else None,
                    'url': download_url  # Прямая ссылка на MP3!
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    # Для этого API ссылка уже есть в results, так что просто перенаправляем
    mp3_url = request.args.get('url')
    if not mp3_url:
        return jsonify({'error': 'no url'}), 400
    
    try:
        audio_response = requests.get(mp3_url, timeout=30)
        return send_file(
            io.BytesIO(audio_response.content),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name="track.mp3"
        )
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
