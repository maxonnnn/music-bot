const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(cors()); // Разрешаем все CORS запросы

// Прокси для скачивания MP3
app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });
    
    try {
        // Получаем ссылку на MP3 через публичный API
        const response = await axios.get(`https://ytdl-python.vercel.app/api/audio?id=${videoId}`);
        const mp3Url = response.data.url;
        
        // Скачиваем MP3 и отдаём плееру
        const audioResponse = await axios.get(mp3Url, { responseType: 'stream' });
        res.setHeader('Content-Type', 'audio/mpeg');
        audioResponse.data.pipe(res);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => console.log('Proxy running on port 3000'));
