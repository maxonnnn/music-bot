const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(cors());

// Прокси для скачивания MP3 через рабочий API
app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });
    
    try {
        // Используем API ytdl-core на Vercel
        const response = await axios.get(`https://ytdl-core-xi.vercel.app/api/info?id=${videoId}`);
        const formats = response.data.formats;
        
        // Находим аудиоформат
        const audioFormat = formats.find(f => f.acodec !== 'none' && f.vcodec === 'none');
        if (!audioFormat) throw new Error('No audio format found');
        
        // Скачиваем MP3 и отдаём плееру
        const audioResponse = await axios.get(audioFormat.url, { responseType: 'stream' });
        res.setHeader('Content-Type', 'audio/mpeg');
        audioResponse.data.pipe(res);
    } catch (error) {
        console.error('Download error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => console.log('Proxy running on port 3000'));
