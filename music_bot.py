from flask import Flask, request, jsonify, send_file
import yt_dlp as youtube_dl
import io
import os

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloaded_%(id)s.%(ext)s',
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ищем и скачиваем трек
            info = ydl.extract_info(f"scsearch:{query}", download=True)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Путь к скачанному файлу
                filename = ydl.prepare_filename(first_result).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                
                # Читаем файл в память
                with open(filename, 'rb') as f:
                    audio_data = f.read()
                
                # Удаляем временный файл
                os.remove(filename)
                
                # Возвращаем MP3 как файл для скачивания
                return send_file(
                    io.BytesIO(audio_data),
                    mimetype='audio/mpeg',
                    as_attachment=True,
                    download_name=f"{first_result.get('title')}.mp3"
                )
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500
    
    return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
