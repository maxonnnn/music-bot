const express = require('express');
const cors = require('cors');
const axios = require('axios');
const fs = require('fs');

const app = express();
app.use(cors());

const YDLS_URL = process.env.YDLS_URL || 'https://ydls-latest-1.onrender.com';
const COOKIE_PATH = process.env.COOKIE_PATH || '/app/cookies.txt'; // путь к кукам

app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });

    const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}`;
    const ydlsUrl = `${YDLS_URL}/mp3/${encodeURIComponent(youtubeUrl)}`;

    try {
        // Передаём куки в ydls через заголовок Cookie
        const cookieHeader = fs.existsSync(COOKIE_PATH) ? fs.readFileSync(COOKIE_PATH, 'utf8') : '';
        
        const response = await axios.get(ydlsUrl, {
            responseType: 'stream',
            headers: cookieHeader ? { Cookie: cookieHeader } : {}
        });

        res.setHeader('Content-Type', 'audio/mpeg');
        response.data.pipe(res);
    } catch (error) {
        console.error('Download error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

app.listen(3000, () => console.log('Proxy running on port 3000'));
