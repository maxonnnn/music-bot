FROM ghcr.io/yeahhub/ytdl-api:latest

EXPOSE 8080

CMD ["node", "server.js"]
