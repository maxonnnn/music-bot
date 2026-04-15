// Импортируем библиотеки
const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Функция, которая будет просить генератор токенов выдать ключ
async function getPoToken(videoId) {
    // Адрес твоего нового сервиса-генератора. Render даст его после деплоя.
    const providerUrl = process.env.POT_PROVIDER_URL || 'http://localhost:4416';
    // Формируем запрос к генератору
    const url = `${providerUrl}/get_pot`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contentBinding: videoId }) // Просим токен для конкретного видео
        });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        return data.poToken;
    } catch (error) {
        console.error('❌ Ошибка получения PO Token:', error.message);
        return null;
    }
}

// Главный эндпоинт для скачивания
app.get('/download', async (req, res) => {
    const videoId = req.query.id;
    if (!videoId) {
        return res.status(400).json({ error: 'no id' });
    }

    console.log(`🎧 Запрос на скачивание: ${videoId}`);

    // 1. ПОЛУЧАЕМ ТОКЕН
    const poToken = await getPoToken(videoId);
    if (!poToken) {
        console.warn(`⚠️ Не удалось получить PO Token для ${videoId}. Пробуем без него.`);
    }

    // 2. ФОРМИРУЕМ КОМАНДУ ДЛЯ yt-dlp
    // Аргументы для yt-dlp
    const ytDlpArgs = [
        '-f', 'bestaudio[ext=m4a]/bestaudio', // Лучшее аудио
        '--extract-audio',                    // Извлечь аудио
        '--audio-format', 'mp3',              // В MP3
        '--audio-quality', '0',               // Качество 0 (лучшее)
        '-o', '-',                            # Вывести в stdout, не создавая файл
        `https://www.youtube.com/watch?v=${videoId}`
    ];

    // Если токен есть, добавляем его в аргументы. Это ключевой момент!
    if (poToken) {
        ytDlpArgs.unshift('--extractor-args', `youtube:po_token=web.gvs+${poToken}`);
        console.log(`✨ Использую PO Token для ${videoId}`);
    } else {
        console.log(`🔑 PO Token не получен, работаю в обычном режиме для ${videoId}`);
    }

    // 3. ЗАПУСКАЕМ yt-dlp
    const ytDlpProcess = spawn('yt-dlp', ytDlpArgs);

    // Устанавливаем заголовки ответа для браузера
    res.setHeader('Content-Disposition', `attachment; filename="${videoId}.mp3"`);
    res.setHeader('Content-Type', 'audio/mpeg');

    // Отправляем поток с аудио напрямую в ответ
    ytDlpProcess.stdout.pipe(res);

    ytDlpProcess.stderr.on('data', (data) => {
        console.error(`[yt-dlp stderr]: ${data}`);
    });

    ytDlpProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`yt-dlp process exited with code ${code}`);
            if (!res.headersSent) {
                res.status(500).json({ error: 'Download failed' });
            }
        } else {
            console.log(`✅ Успешно скачано и отправлено: ${videoId}`);
        }
    });
});

// Запускаем сервер
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`🚀 Сервер готов к работе на порту ${port}`);
});
