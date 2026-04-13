from flask import Flask, request, jsonify, send_file
import yt_dlp as youtube_dl
import os
import subprocess

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
        'outtmpl': 'downloaded_%(id)s.%(ext)s',
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Ищем трек
            info = ydl.extract_info(f"scsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Получаем ссылку на аудио
                audio_url = None
                if 'formats' in first_result:
                    for f in first_result['formats']:
                        if f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                            audio_url = f.get('url')
                            break
                
                if not audio_url:
                    audio_url = first_result.get('url')
                
                # Скачиваем через yt-dlp с конвертацией в MP3
                ydl_opts_dl = {
                    'format': 'bestaudio/best',
                    'quiet': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': 'downloaded_%(id)s.%(ext)s',
                }
                
                with youtube_dl.YoutubeDL(ydl_opts_dl) as ydl_dl:
                    # Скачиваем и конвертируем
                    ydl_dl.download([first_result['webpage_url']])
                    
                    # Находим скачанный файл
                    for file in os.listdir('.'):
                        if file.startswith('downloaded_') and file.endswith('.mp3'):
                            # Отправляем файл
                            with open(file, 'rb') as f:
                                audio_data = f.read()
                            os.remove(file)
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
