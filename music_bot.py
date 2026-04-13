from flask import Flask, request, jsonify
import yt_dlp as youtube_dl

app = Flask(__name__)

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': True,
}

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                return jsonify({
                    'title': first_result.get('title'),
                    'url': first_result.get('url_duration', [{}])[0].get('url'),
                    'duration': first_result.get('duration')
                })
        except Exception:
            return jsonify({'error': 'search failed'}), 500
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
