from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app)

# Публичный прокси для JioSaavn
PROXY_API = "https://jiosaavn-api.vercel.app"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    try:
        response = requests.get(f"{PROXY_API}/api/search?query={query}&limit=10", timeout=15)
        data = response.json()
        
        results = []
        if 'data' in data and 'results' in data['data']:
            for song in data['data']['results']:
                results.append({
                    'id': song.get('id'),
                    'title': song.get('name'),
                    'artist': song.get('artists', {}).get('primary', [{}])[0].get('name') if song.get('artists') else 'Unknown',
                    'duration': song.get('duration'),
                    'thumbnail': song.get('image', [{}])[2].get('link') if song.get('image') else None,
                    'url': f"/download?id={song.get('id')}"
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
        response = requests.get(f"{PROXY_API}/api/songs/{song_id}", timeout=15)
        data = response.json()
        
        if 'data' in data and 'downloadUrl' in data['data']:
            mp3_url = data['data']['downloadUrl'][4]['link']
            audio_response = requests.get(mp3_url, timeout=30)
            return send_file(
                io.BytesIO(audio_response.content),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"{song_id}.mp3"
            )
        else:
            return jsonify({'error': 'no mp3 url'}), 500
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
