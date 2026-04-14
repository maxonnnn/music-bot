from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp as youtube_dl
import os
import time

app = Flask(__name__)
CORS(app)

# Расширенные настройки для обхода блокировок YouTube
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    # Указываем использовать Deno для решения JS-задач
    'js_runtimes': {'deno': {}},
    # Указываем файл с куками
    # 'cookiefile': 'cookies.txt',
    # Скачиваем и конвертируем в MP3
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'downloaded_%(id)s.%(ext)s',
}

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ищем ТОЛЬКО первый результат (ytsearch1)
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]

                # Ищем скачанный MP3 файл
                downloaded_file = None
                for file in os.listdir('.'):
                    if file.startswith('downloaded_') and file.endswith('.mp3'):
                        downloaded_file = file
                        break

                if downloaded_file:
                    # Отправляем файл плееру
                    return send_file(
                        downloaded_file,
                        mimetype='audio/mpeg',
                        as_attachment=True,
                        download_name=f"{first_result.get('uploader')} - {first_result.get('title')}.mp3"
                    )
                else:
                    return jsonify({'error': 'download failed: file not found'}), 500

        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500

    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
