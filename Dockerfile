FROM python:3.10-slim

RUN pip install flask flask-cors requests gunicorn

WORKDIR /app
COPY music_bot.py .

CMD ["gunicorn", "music_bot:app", "--bind", "0.0.0.0:10000"]
