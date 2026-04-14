from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from jiosaavn import JioSaavn
import asyncio
import io
import requests

app = Flask(__name__)
CORS(app)

# Создаём клиент JioSaavn
saavn = JioSaavn()

def run_async(coro):
    """Запускает асинхронную функцию"""
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
        # Поиск песен [citation:6][citation:8]
        results = run_async(saavn.search_songs(query))
        
        if results and len(results) > 0:
            # Форматируем результаты
            tracks = []
            for item in results[:10]:  # максимум 10 треков
                # Получаем прямую ссылку на MP3 [citation:6]
                song_id = item.get('id') or item.get('url')
                if song_id:
                    try:
                        link_data = run_async(saavn.get_song_direct_link(song_id))
                        mp3_url = link_data.get('link') if link_data else None
                    except:
                        mp3_url = None
                else:
                    mp3_url = None
                
                tracks.append({
                    'id': item.get('id'),
                    'title': item.get('song') or item.get('title'),
                    'artist': item.get('primary_artists') or item.get('artist'),
                    'album': item.get('album'),
                    'duration': item.get('duration'),
                    'url': mp3_url,
                    'thumbnail': item.get('image')
                })
            
            return jsonify(tracks)
        return jsonify([])
    
    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500

@app.route('/download')
def download():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'no url'}), 400
    
    try:
        # Скачиваем MP3 через requests
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return send_file(
                io.BytesIO(response.content),
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name='track.mp3'
            )
        else:
            return jsonify({'error': 'download failed'}), 500
    except Exception as e:
        return jsonify({'error': f'download error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
