# Dockerfile.app
FROM client:base

# Aseguramos que el directorio de trabajo es el mismo
WORKDIR /app

# Copiamos el código de la aplicación
COPY client/ /app/client/

RUN chmod +x ./startup.sh

CMD ["sh", "-c", "/app/startup.sh && tail -f /dev/null"]

# CMD ["streamlit", "run", "app.py"]


