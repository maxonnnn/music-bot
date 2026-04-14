from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
import io

app = Flask(__name__)
CORS(app)

# Источники из SoundBound
SOURCES = {
    'saavn': {
        'search': 'https://www.jiosaavn.com/api.php?__call=autocomplete.get&ctx=wap6&query={query}&_format=json&_marker=0&api_version=4',
        'download': 'https://www.jiosaavn.com/api.php?__call=song.getDetails&ctx=wap6&pids={id}&_format=json&_marker=0&api_version=4',
    },
    'soundcloud': {
        'search': 'https://api-v2.soundcloud.com/search/tracks?q={query}&client_id=YOUR_CLIENT_ID&limit=10',
    },
    'jamendo': {
        'search': 'https://api.jamendo.com/v3.0/tracks?client_id=ca29f9b5&format=json&limit=10&search={query}&audioformat=mp32',
        'download': 'https://api.jamendo.com/v3.0/tracks/file?client_id=ca29f9b5&id={id}',
    },
    'gaana': {
        'search': 'https://gaana.com/autocomplete?query={query}',
    }
}

@app.route('/search')
def search():
    query = request.args.get('query')
    source = request.args.get('source', 'saavn')  # saavn, jamendo, soundcloud
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    results = []
    
    # 1. JioSaavn (работает без ключа)
    if source == 'saavn':
        try:
            url = SOURCES['saavn']['search'].format(query=query)
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'songs' in data and data['songs']['data']:
                for song in data['songs']['data']:
                    results.append({
                        'id': song.get('id'),
                        'title': song.get('title'),
                        'artist': song.get('more_info', {}).get('primary_artists'),
                        'album': song.get('more_info', {}).get('album'),
                        'duration': song.get('more_info', {}).get('duration'),
                        'thumbnail': song.get('image'),
                        'source': 'saavn',
                        'url': f"/download?source=saavn&id={song.get('id')}"
                    })
        except Exception as e:
            print(f"Saavn error: {e}")
    
    # 2. Jamendo (бесплатная легальная музыка, работает отлично)
    if source == 'jamendo':
        try:
            url = SOURCES['jamendo']['search'].format(query=query)
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'results' in data:
                for track in data['results'][:10]:
                    results.append({
                        'id': track.get('id'),
                        'title': track.get('name'),
                        'artist': track.get('artist_name'),
                        'album': track.get('album_name'),
                        'duration': track.get('duration'),
                        'thumbnail': track.get('image'),
                        'source': 'jamendo',
                        'url': f"/download?source=jamendo&id={track.get('id')}"
                    })
        except Exception as e:
            print(f"Jamendo error: {e}")
    
    return jsonify(results)

@app.route('/download')
def download():
    source = request.args.get('source', 'saavn')
    song_id = request.args.get('id')
    
    if not song_id:
        return jsonify({'error': 'no id'}), 400
    
    mp3_url = None
    
    # JioSaavn download
    if source == 'saavn':
        try:
            url = SOURCES['saavn']['download'].format(id=song_id)
            response = requests.get(url, timeout=15)
            data = response.json()
            
            if data and song_id in data:
                mp3_url = data[song_id].get('more_info', {}).get('encrypted_media_url')
        except Exception as e:
            return jsonify({'error': f'Saavn error: {str(e)}'}), 500
    
    # Jamendo download (прямая ссылка на MP3)
    elif source == 'jamendo':
        try:
            mp3_url = SOURCES['jamendo']['download'].format(id=song_id)
        except Exception as e:
            return jsonify({'error': f'Jamendo error: {str(e)}'}), 500
    
    if mp3_url:
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
    
    return jsonify({'error': 'no download url'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
