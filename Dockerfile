FROM python:3.10-slim

# Устанавливаем Deno и FFmpeg
RUN apt-get update && apt-get install -y curl unzip ffmpeg
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install yt-dlp flask flask-cors gunicorn

WORKDIR /app
COPY . .

RUN deno --version

CMD ["gunicorn", "music_bot:app", "--bind", "0.0.0.0:10000"]
