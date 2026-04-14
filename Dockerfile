FROM python:3.10-slim

# Устанавливаем Deno (нужен для решения JS-вызовов YouTube)
RUN apt-get update && apt-get install -y curl unzip
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# Устанавливаем yt-dlp-nightly (последняя версия с фиксами)
RUN pip install --upgrade pip
RUN pip install yt-dlp-nightly flask flask-cors gunicorn

WORKDIR /app
COPY . .

# Убеждаемся, что Deno доступен для yt-dlp
RUN deno --version

CMD ["gunicorn", "music_bot:app", "--bind", "0.0.0.0:10000"]
