from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp as youtube_dl

app = Flask(__name__)
CORS(app)

# Опции для yt-dlp с попыткой обойти блокировку YouTube
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': False,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
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
            # Ищем первый результат
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]

                # Получаем ссылку на аудиопоток
                audio_url = first_result.get('url')
                if not audio_url and 'formats' in first_result:
                    for f in first_result['formats']:
                        if f.get('vcodec') == 'none':
                            audio_url = f.get('url')
                            break

                return jsonify({
                    'title': first_result.get('title'),
                    'artist': first_result.get('uploader'),
                    'url': audio_url,
                    'duration': first_result.get('duration'),
                    'thumbnail': first_result.get('thumbnail')
                })
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500

    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
