from flask import Flask, request, jsonify
import yt_dlp as youtube_dl

app = Flask(__name__)

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': False,  # Меняем на False, чтобы получить полную информацию
}

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ищем видео
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Пробуем получить прямую ссылку на аудио
                audio_url = None
                
                # Вариант 1: если есть форматы
                if 'formats' in first_result:
                    # Ищем лучший аудиоформат (обычно m4a или webm)
                    for f in first_result['formats']:
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                            audio_url = f.get('url')
                            break
                    # Если не нашли чистый аудио, берем первый с аудио
                    if not audio_url:
                        for f in first_result['formats']:
                            if f.get('acodec') != 'none':
                                audio_url = f.get('url')
                                break
                
                # Вариант 2: прямая ссылка из url
                if not audio_url:
                    audio_url = first_result.get('url')
                
                return jsonify({
                    'title': first_result.get('title'),
                    'url': audio_url,
                    'duration': first_result.get('duration')
                })
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
