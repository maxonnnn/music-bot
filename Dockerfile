FROM ghcr.io/matthewzhaocc/ytdl-api:latest

EXPOSE 8080

CMD ["node", "server.js"]
