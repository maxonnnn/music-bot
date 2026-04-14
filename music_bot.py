from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp as youtube_dl
import os

app = Flask(__name__)
CORS(app)

# Опции для yt-dlp с использованием кук и обходом блокировок
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': False,
    'cookiefile': 'cookies.txt',  # Используем универсальные куки
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

    # Извлекаем ID видео из ссылки или ищем
    video_id = query
    if 'youtube.com/watch?v=' in query:
        video_id = query.split('v=')[1].split('&')[0]
    elif 'youtu.be/' in query:
        video_id = query.split('youtu.be/')[1].split('?')[0]

    # Если это поисковый запрос, находим ID первого результата
    if len(video_id) != 11:
        with youtube_dl.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if 'entries' in info and info['entries']:
                video_id = info['entries'][0]['id']
            else:
                return jsonify({'error': 'not found'}), 404

    video_url = f"https://www.youtube.com/watch?v={video_id}"

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([video_url])
            
            # Находим скачанный файл
            downloaded_file = None
            for file in os.listdir('.'):
                if file.startswith('downloaded_') and file.endswith('.mp3'):
                    downloaded_file = file
                    break
            
            if downloaded_file:
                return send_file(
                    downloaded_file,
                    mimetype='audio/mpeg',
                    as_attachment=True,
                    download_name=f"track.mp3"
                )
            else:
                return jsonify({'error': 'download failed'}), 500
                
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
