const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const app = express();

app.use(cors());
app.use(express.json());

// Адрес генератора токенов (замени на свой адрес)
const POT_PROVIDER_URL = 'https://pot-provider-hi22.onrender.com'; // ⚠️ ЗАМЕНИ НА СВОЙ!

// Функция получения PO токена
async function getPoToken(videoId) {
    try {
        const response = await fetch(`${POT_PROVIDER_URL}/get_pot`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();
        return data.poToken;
    } catch (error) {
        console.error('PO Token error:', error.message);
        return null;
    }
}

app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) return res.status(400).json({ error: 'no id' });

    const poToken = await getPoToken(videoId);
    
    const args = [
        '-f', 'bestaudio[ext=m4a]/bestaudio',
        '--extract-audio',
        '--audio-format', 'mp3',
        '-o', '-',
        `https://www.youtube.com/watch?v=${videoId}`
    ];
    
    if (poToken) {
        args.unshift('--extractor-args', `youtube:po_token=web.gvs+${poToken}`);
        console.log(`✅ Использую PO Token для ${videoId}`);
    }
    
    const ytdlp = spawn('yt-dlp', args);
    res.setHeader('Content-Type', 'audio/mpeg');
    ytdlp.stdout.pipe(res);
    
    ytdlp.stderr.on('data', (data) => console.error(`[yt-dlp] ${data}`));
    ytdlp.on('close', (code) => {
        if (code !== 0) console.error(`yt-dlp exit code: ${code}`);
    });
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server on port ${port}`));
