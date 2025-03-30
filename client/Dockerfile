# client/Dockerfile.app
FROM client:base

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir markdown

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501 || exit 1

RUN chmod +x ./startup.sh

ENTRYPOINT ["./startup.sh"]
