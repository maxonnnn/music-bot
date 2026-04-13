from flask import Flask, request, jsonify, send_file
import yt_dlp as youtube_dl
import io
import re
from sclib import SoundcloudAPI, Track

app = Flask(__name__)
api = SoundcloudAPI()

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', '', name)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    ydl_opts = {'quiet': True, 'extract_flat': False}
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"scsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Получаем ссылку на страницу трека (нужна для soundcloud-lib)
                webpage_url = first_result.get('webpage_url')
                
                return jsonify({
                    'id': first_result.get('id'),
                    'title': first_result.get('title'),
                    'artist': first_result.get('uploader'),
                    'url': webpage_url,  # ссылка на страницу SoundCloud
                    'duration': first_result.get('duration'),
                    'thumbnail': first_result.get('thumbnail')
                })
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500
    
    return jsonify({'error': 'not found'}), 404

@app.route('/download')
def download():
    track_url = request.args.get('url')
    if not track_url:
        return jsonify({'error': 'no url'}), 400
    
    try:
        # soundcloud-lib скачивает MP3
        track = api.resolve(track_url)
        
        if not isinstance(track, Track):
            return jsonify({'error': 'url is not a track'}), 400
        
        # Скачиваем MP3 в память
        mp3_data = track.get_mp3()
        
        safe_title = sanitize_filename(track.title)
        filename = f"{track.artist} - {safe_title}.mp3"
        
        return send_file(
            io.BytesIO(mp3_data),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': f'download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
