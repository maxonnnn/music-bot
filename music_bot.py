from flask import Flask, request, jsonify
import yt_dlp as youtube_dl

app = Flask(__name__)

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ищем на SoundCloud
            info = ydl.extract_info(f"scsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Пробуем получить ссылку на MP3
                audio_url = None
                
                # Сначала ищем в форматах
                if 'formats' in first_result:
                    for f in first_result['formats']:
                        # Ищем MP3 или прямой аудиоформат
                        if f.get('ext') in ['mp3', 'm4a', 'aac']:
                            audio_url = f.get('url')
                            break
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                            audio_url = f.get('url')
                            if audio_url and not audio_url.endswith('.m3u8'):
                                break
                
                if not audio_url:
                    audio_url = first_result.get('url')
                
                # Если ссылка ведёт на плейлист, добавляем параметр для конвертации
                if audio_url and audio_url.endswith('.m3u8'):
                    # Заменяем на возможную MP3-ссылку
                    audio_url = audio_url.replace('/playlist.m3u8', '.mp3')
                
                return jsonify({
                    'title': first_result.get('title'),
                    'artist': first_result.get('uploader'),
                    'url': audio_url,
                    'duration': first_result.get('duration')
                })
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
