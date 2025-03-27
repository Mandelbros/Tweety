# client/Dockerfile.app
FROM client:base

WORKDIR /app

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501 || exit 1

RUN chmod +x ./startup.sh
# RUN chmod +x ./client/startup.sh

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
