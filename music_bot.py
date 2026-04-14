from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io
import base64

app = Flask(__name__)
CORS(app)

# Spotify API credentials (публичные, для демонстрации)
CLIENT_ID = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
CLIENT_SECRET = "q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h6"

def get_spotify_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"grant_type": "client_credentials"}
    result = requests.post(url, headers=headers, data=data)
    return result.json().get("access_token")

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    search_url = f"https://api.spotify.com/v1/search?q={query}&type=track&limit=10"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        data = response.json()
        
        results = []
        if 'tracks' in data and 'items' in data['tracks']:
            for track in data['tracks']['items']:
                # Spotify даёт 30-секундное превью для бесплатных аккаунтов
                preview_url = track.get('preview_url')
                results.append({
                    'id': track['id'],
                    'title': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'duration': track['duration_ms'] // 1000,
                    'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'url': preview_url,  # 30-секундное превью
                    'is_preview': True
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    track_url = request.args.get('url')
    if not track_url:
        return jsonify({'error': 'no url'}), 400
    
    try:
        response = requests.get(track_url, timeout=30)
        return send_file(
            io.BytesIO(response.content),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name="track.mp3"
        )
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
