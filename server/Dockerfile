FROM server:base

WORKDIR /app

COPY . /app

RUN chmod +x ./startup.sh

ENTRYPOINT ["./startup.sh"]