# server/Dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH="/app"

COPY server/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ /app/server/

CMD ["python", "-m", "server.main"]