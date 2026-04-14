FROM python:3.10-slim

# Устанавливаем зависимости
RUN pip install flask flask-cors jiosaavn-python requests gunicorn

WORKDIR /app
COPY music_bot.py .

CMD ["gunicorn", "music_bot:app", "--bind", "0.0.0.0:10000"]
