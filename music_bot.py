from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp as youtube_dl
import os

app = Flask(__name__)
CORS(app)

# Добавляем Deno и правильные параметры
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': False,
    'cookiefile': 'cookies.txt',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloaded_%(id)s.%(ext)s',
    'extractor_args': {
        'youtube': {
            'player_client': ['ios', 'web'],  # android удалён — он сломан [citation:4]
        }
    }
}

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if 'entries' in info and info['entries']:
                for file in os.listdir('.'):
                    if file.startswith('downloaded_') and file.endswith('.mp3'):
                        return send_file(
                            file,
                            mimetype='audio/mpeg',
                            as_attachment=True,
                            download_name="track.mp3"
                        )
                return jsonify({'error': 'download failed'}), 500
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500

    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
