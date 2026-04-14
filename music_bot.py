from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app)

JAMENDO_API = "https://api.jamendo.com/v3.0/tracks"
JAMENDO_CLIENT_ID = "ca29f9b5"  # Публичный ID

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    params = {
        'client_id': JAMENDO_CLIENT_ID,
        'format': 'json',
        'limit': 10,
        'search': query,
        'audioformat': 'mp32'
    }
    
    try:
        response = requests.get(JAMENDO_API, params=params, timeout=15)
        data = response.json()
        
        results = []
        if 'results' in data:
            for track in data['results']:
                results.append({
                    'id': track.get('id'),
                    'title': track.get('name'),
                    'artist': track.get('artist_name'),
                    'album': track.get('album_name'),
                    'duration': track.get('duration'),
                    'thumbnail': track.get('image'),
                    'url': f"/download?id={track.get('id')}"
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    track_id = request.args.get('id')
    if not track_id:
        return jsonify({'error': 'no id'}), 400
    
    # Jamendo отдаёт прямую ссылку на MP3
    mp3_url = f"https://api.jamendo.com/v3.0/tracks/file?client_id={JAMENDO_CLIENT_ID}&id={track_id}"
    
    try:
        audio_response = requests.get(mp3_url, timeout=30)
        return send_file(
            io.BytesIO(audio_response.content),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f"{track_id}.mp3"
        )
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
