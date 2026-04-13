from flask import Flask, request, jsonify
import yt_dlp as youtube_dl

app = Flask(__name__)

# Опции для yt-dlp: только поиск, без скачивания
ydl_opts = {
    'quiet': True,
    'extract_flat': False,
}

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ищем трек на SoundCloud
            info = ydl.extract_info(f"scsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]

                # Пытаемся найти прямую ссылку на MP3
                audio_url = None
                if 'formats' in first_result:
                    for f in first_result['formats']:
                        # Ищем ссылку, которая ведет на .mp3 или не является .m3u8
                        if f.get('ext') == 'mp3' or (f.get('vcodec') == 'none' and not f.get('url', '').endswith('.m3u8')):
                            audio_url = f.get('url')
                            break

                if not audio_url:
                    audio_url = first_result.get('url')

                return jsonify({
                    'title': first_result.get('title'),
                    'artist': first_result.get('uploader'),
                    'url': audio_url,  # Прямая ссылка для скачивания
                    'duration': first_result.get('duration')
                })
        except Exception as e:
            # Логируем ошибку на сервере
            print(f"Error: {e}")
            return jsonify({'error': f'search failed: {str(e)}'}), 500

    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
