from flask import Flask, request, send_file, jsonify
import yt_dlp as youtube_dl
import io
import os

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    # Опции для yt-dlp — скачиваем лучшее аудио и конвертируем в MP3
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloaded_%(id)s.%(ext)s',
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ищем трек на SoundCloud
            info = ydl.extract_info(f"scsearch:{query}", download=True)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Путь к скачанному MP3
                base = ydl.prepare_filename(first_result).rsplit('.', 1)[0]
                mp3_path = f"{base}.mp3"
                
                if os.path.exists(mp3_path):
                    # Отправляем MP3 как файл для скачивания
                    return send_file(
                        mp3_path,
                        mimetype='audio/mpeg',
                        as_attachment=True,
                        download_name=f"{first_result.get('title')}.mp3"
                    )
                else:
                    return jsonify({'error': 'file not found'}), 500
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
