const express = require('express');
const cors = require('cors');
const ytdl = require('@distube/ytdl-core');

const app = express();
app.use(cors());

app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });
    
    const url = `https://www.youtube.com/watch?v=${videoId}`;
    
    try {
        // Получаем информацию о видео
        const info = await ytdl.getInfo(url);
        
        // Выбираем аудиоформат с помощью chooseFormat [citation:2]
        const audioFormat = ytdl.chooseFormat(info.formats, { 
            quality: 'highestaudio',
            filter: 'audioonly' 
        });
        
        if (!audioFormat) throw new Error('No audio format found');
        
        // Скачиваем и отдаём потоком
        res.setHeader('Content-Type', 'audio/mpeg');
        ytdl(url, { format: audioFormat }).pipe(res);
        
    } catch (error) {
        console.error('Download error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => console.log('Server running'));
