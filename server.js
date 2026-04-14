const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
app.use(cors());

// Список API для получения ссылок на MP3
const AUDIO_APIS = [
    async (id) => {
        const res = await axios.get(`https://ytdl-core-xi.vercel.app/api/info?id=${id}`);
        const audio = res.data.formats.find(f => f.acodec !== 'none' && f.vcodec === 'none');
        return audio?.url;
    },
    async (id) => {
        const res = await axios.get(`https://ytdl-python.vercel.app/api/audio?id=${id}`);
        return res.data.url;
    },
    async (id) => {
        const res = await axios.get(`https://yt-api.mbaraa.xyz/api/audio/${id}`);
        return res.data.url;
    },
    async (id) => {
        // Прямой запрос к YouTube через ytdl-core (работает без API)
        const ytdl = require('ytdl-core');
        const info = await ytdl.getInfo(id);
        const audio = info.formats.find(f => f.acodec !== 'none' && f.vcodec === 'none');
        return audio?.url;
    }
];

app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });
    
    for (const api of AUDIO_APIS) {
        try {
            const mp3Url = await api(videoId);
            if (mp3Url && mp3Url.startsWith('http')) {
                const audioResponse = await axios.get(mp3Url, { responseType: 'stream' });
                res.setHeader('Content-Type', 'audio/mpeg');
                return audioResponse.data.pipe(res);
            }
        } catch (err) {
            console.log(`API failed: ${err.message}`);
        }
    }
    
    res.status(500).json({ error: 'No working audio API found' });
});

app.listen(3000, () => console.log('Proxy running on port 3000'));
