FROM python:3.10-slim

# Устанавливаем Deno
RUN apt-get update && apt-get install -y curl unzip
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "music_bot:app", "--bind", "0.0.0.0:10000"]
