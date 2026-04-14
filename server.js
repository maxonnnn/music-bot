const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(cors());

// Прокси для любого URL
app.get('/proxy', async (req, res) => {
    const targetUrl = req.query.url;
    if (!targetUrl) return res.status(400).json({ error: 'no url' });
    
    try {
        const response = await axios.get(targetUrl, { responseType: 'arraybuffer' });
        res.set('Access-Control-Allow-Origin', '*');
        res.send(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Скачивание MP3 через ytdl
app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });
    
    try {
        const ytdl = require('ytdl-core');
        const info = await ytdl.getInfo(videoId);
        const audioFormat = info.formats.find(f => f.hasAudio && !f.hasVideo);
        
        res.set('Access-Control-Allow-Origin', '*');
        ytdl(videoId, { format: audioFormat }).pipe(res);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => console.log('Proxy running'));
