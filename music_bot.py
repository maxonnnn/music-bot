from flask import Flask, request, jsonify, send_file
import yt_dlp as youtube_dl
import io
import os
import uuid

app = Flask(__name__)

@app.route('/search')
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'no query'}), 400
    
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"scsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                first_result = info['entries'][0]
                
                # Получаем m3u8 ссылку
                m3u8_url = None
                if 'formats' in first_result:
                    for f in first_result['formats']:
                        if f.get('vcodec') == 'none':
                            m3u8_url = f.get('url')
                            break
                
                if not m3u8_url:
                    m3u8_url = first_result.get('url')
                
                return jsonify({
                    'id': first_result.get('id'),
                    'title': first_result.get('title'),
                    'artist': first_result.get('uploader'),
                    'url': m3u8_url,  # m3u8 ссылка для онлайн-прослушивания
                    'duration': first_result.get('duration'),
                    'thumbnail': first_result.get('thumbnail')
                })
        except Exception as e:
            return jsonify({'error': f'search failed: {str(e)}'}), 500
    
    return jsonify({'error': 'not found'}), 404

@app.route('/download')
def download():
    m3u8_url = request.args.get('url')
    if not m3u8_url:
        return jsonify({'error': 'no url'}), 400
    
    # Генерируем уникальное имя файла
    filename = f"download_{uuid.uuid4().hex}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            # Скачиваем и конвертируем
            ydl.download([m3u8_url])
            
            # Находим готовый MP3
            mp3_path = filename.replace('.%(ext)s', '.mp3')
            if not os.path.exists(mp3_path):
                mp3_path = filename + '.mp3'
            
            if os.path.exists(mp3_path):
                return send_file(
                    mp3_path,
                    mimetype='audio/mpeg',
                    as_attachment=True,
                    download_name=mp3_path
                )
            else:
                return jsonify({'error': 'file not found'}), 500
        except Exception as e:
            return jsonify({'error': f'download failed: {str(e)}'}), 500
        finally:
            # Удаляем временные файлы
            for f in os.listdir('.'):
                if f.startswith('download_'):
                    try:
                        os.remove(f)
                    except:
                        pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
