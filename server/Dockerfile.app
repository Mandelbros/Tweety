# Dockerfile.app
FROM server:base

# Aseguramos que el directorio de trabajo es el mismo
WORKDIR /app

# Copiamos el código de la aplicación
COPY server/ /app/server/

# Definimos el comando para ejecutar la aplicación
CMD ["python", "-m", "server.main"]

