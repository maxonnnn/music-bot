const express = require('express');
const cors = require('cors');
const ytdl = require('ytdl-core');

const app = express();
app.use(cors());

app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) {
        return res.status(400).json({ error: 'no id' });
    }
    
    try {
        const info = await ytdl.getInfo(videoId);
        const audioFormat = ytdl.chooseFormat(info.formats, { 
            quality: 'highestaudio',
            filter: 'audioonly'
        });
        
        if (!audioFormat) {
            throw new Error('No audio format found');
        }
        
        res.header('Content-Type', 'audio/mpeg');
        ytdl(videoId, { format: audioFormat }).pipe(res);
        
    } catch (error) {
        console.error('Download error:', error.message);
        res.status(500).json({ error: error.message });
    }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Proxy running on port ${port}`));
