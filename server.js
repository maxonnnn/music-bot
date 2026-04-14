const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();

// Настройки CORS — разрешаем всё
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['*']
}));

// Обрабатываем preflight запросы
app.options('*', cors());

// Прокси для скачивания MP3
app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });
    
    // Добавляем CORS заголовки вручную
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    
    try {
        // Пробуем получить MP3 через несколько источников
        let mp3Url = null;
        
        // Источник 1: ytdl-core API
        try {
            const infoRes = await axios.get(`https://ytdl-core-xi.vercel.app/api/info?id=${videoId}`);
            const audio = infoRes.data.formats.find(f => f.acodec !== 'none' && f.vcodec === 'none');
            if (audio) mp3Url = audio.url;
        } catch (e) {}
        
        // Источник 2: ytdl-python
        if (!mp3Url) {
            try {
                const audioRes = await axios.get(`https://ytdl-python.vercel.app/api/audio?id=${videoId}`);
                mp3Url = audioRes.data.url;
            } catch (e) {}
        }
        
        // Источник 3: прямой запрос к YouTube
        if (!mp3Url) {
            const ytdl = require('ytdl-core');
            const info = await ytdl.getInfo(videoId);
            const audio = info.formats.find(f => f.acodec !== 'none' && f.vcodec === 'none');
            mp3Url = audio?.url;
        }
        
        if (mp3Url) {
            const audioResponse = await axios.get(mp3Url, { responseType: 'stream' });
            res.setHeader('Content-Type', 'audio/mpeg');
            return audioResponse.data.pipe(res);
        }
        
        res.status(500).json({ error: 'No audio found' });
    } catch (error) {
        console.error('Download error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => console.log('Proxy running on port 3000'));
