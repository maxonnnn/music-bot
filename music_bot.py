from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io
import time

app = Flask(__name__)
CORS(app)

# Список публичных инстансов Piped API (работают в РФ)
PIPED_INSTANCES = [
    "https://pipedapi.adminforge.de",
    "https://pipedapi.projectsegfau.lt",
    "https://pipedapi.moomoo.me",
    "https://pipedapi.kavin.rocks",
]

def get_working_instance():
    """Находит работающий инстанс Piped API"""
    for instance in PIPED_INSTANCES:
        try:
            response = requests.get(f"{instance}/search?q=test&filter=music_songs", timeout=5)
            if response.status_code == 200:
                return instance
        except:
            continue
    return PIPED_INSTANCES[0]  # возвращаем первый, если все падают

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    instance = get_working_instance()
    
    try:
        search_url = f"{instance}/search?q={query}&filter=music_songs"
        response = requests.get(search_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'items' in data:
            for item in data['items'][:10]:
                video_id = item['url'].split('watch?v=')[1]
                results.append({
                    'id': video_id,
                    'title': item['title'],
                    'artist': item['uploaderName'],
                    'duration': item['duration'],
                    'thumbnail': item['thumbnail'],
                    'url': f"https://music-bot.onrender.com/download?id={video_id}"
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'no id'}), 400
    
    instance = get_working_instance()
    
    try:
        stream_url = f"{instance}/streams/{video_id}"
        response = requests.get(stream_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if 'audioStreams' in data and len(data['audioStreams']) > 0:
            mp3_url = data['audioStreams'][0]['url']
            audio_response = requests.get(mp3_url, timeout=30)
            return send_file(
                io.BytesIO(audio_response.content),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"{video_id}.mp3"
            )
        else:
            return jsonify({'error': 'no audio streams found'}), 500
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
