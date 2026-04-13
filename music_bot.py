from flask import Flask, request, send_file, jsonify
from sclib import SoundcloudAPI, Track
import io
import re

app = Flask(__name__)
api = SoundcloudAPI()

def sanitize_filename(name: str) -> str:
    """Убирает из имени файла недопустимые символы."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400

    try:
        # Ищем трек через API
        tracks = api.search(query)
        if not tracks:
            return jsonify({'error': 'not found'}), 404

        track = tracks[0]
        return jsonify({
            'id': track.id,
            'title': track.title,
            'artist': track.artist,
            'duration': track.duration,
            'thumbnail': track.artwork_url
        })

    except Exception as e:
        return jsonify({'error': f'search failed: {str(e)}'}), 500


@app.route('/download')
def download():
    track_url = request.args.get('url')
    if not track_url:
        return jsonify({'error': 'no url'}), 400

    try:
        # Получаем трек по URL и скачиваем его в MP3
        track = api.resolve(track_url)

        if not isinstance(track, Track):
            return jsonify({'error': 'url is not a track'}), 400

        # Скачиваем MP3 в память
        track_mp3 = track.get_mp3()

        safe_title = sanitize_filename(track.title)
        filename = f"{track.artist} - {safe_title}.mp3"

        return send_file(
            io.BytesIO(track_mp3),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': f'download failed: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
