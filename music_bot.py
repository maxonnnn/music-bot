from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app)

PIPED_API = "https://pipedapi.kavin.rocks"

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    try:
        search_url = f"{PIPED_API}/search?q={query}&filter=music_songs"
        response = requests.get(search_url)
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
        return jsonify({'error': str(e)}), 500

@app.route('/download')
def download():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'no id'}), 400
    
    try:
        stream_url = f"{PIPED_API}/streams/{video_id}"
        response = requests.get(stream_url)
        data = response.json()
        
        if 'audioStreams' in data and len(data['audioStreams']) > 0:
            mp3_url = data['audioStreams'][0]['url']
            audio_response = requests.get(mp3_url)
            return send_file(
                io.BytesIO(audio_response.content),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"{video_id}.mp3"
            )
        else:
            return jsonify({'error': 'no audio found'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
