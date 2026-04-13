from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp as youtube_dl

app = Flask(__name__)
CORS(app)  # Разрешаем все CORS запросы

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
            info = ydl.extract_info(f"scsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Получаем ссылку на страницу трека
                webpage_url = first_result.get('webpage_url')
                
                return jsonify({
                    'id': first_result.get('id'),
                    'title': first_result.get('title'),
                    'artist': first_result.get('uploader'),
                    'url': webpage_url,
                    'duration': first_result.get('duration'),
                    'thumbnail': first_result.get('thumbnail')
                })
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
