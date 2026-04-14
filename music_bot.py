from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from jiosaavn import JioSaavn
import asyncio
import io
import requests

app = Flask(__name__)
CORS(app)

saavn = JioSaavn()

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    try:
        results = run_async(saavn.search_songs(query))
        
        if results and len(results) > 0:
            tracks = []
            for item in results[:10]:
                tracks.append({
                    'id': item.get('id'),
                    'title': item.get('song') or item.get('title'),
                    'artist': item.get('primary_artists') or item.get('artist'),
                    'duration': item.get('duration'),
                    'url': f"https://music-bot.onrender.com/download?id={item.get('id')}",
                    'thumbnail': item.get('image')
                })
            return jsonify(tracks)
        return jsonify([])
    
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    song_id = request.args.get('id')
    if not song_id:
        return jsonify({'error': 'no id'}), 400
    
    try:
        link_data = run_async(saavn.get_song_direct_link(song_id))
        mp3_url = link_data.get('link')
        
        if mp3_url:
            response = requests.get(mp3_url, timeout=30)
            return send_file(
                io.BytesIO(response.content),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='track.mp3'
            )
        else:
            return jsonify({'error': 'no link'}), 500
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
