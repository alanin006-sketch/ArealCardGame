# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV BOT_TOKEN=8135923353:AAF5stVsDOtdZBRmrMguf7AomzBuAnaiq7c
ENV DATABASE_URL=sqlite+aiosqlite:///./data/game.db

EXPOSE 8000

CMD ["python", "main.py"]
