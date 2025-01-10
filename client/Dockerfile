# client/Dockerfile
FROM python:3.12-alpine

WORKDIR /app

# Install iproute2 and other required packages
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 iputils-ping && rm -rf /var/lib/apt/lists/*

COPY client/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY client/ .

RUN chmod +x ./startup.sh

CMD ["sh", "-c", "/app/startup.sh && tail -f /dev/null"]

# CMD ["streamlit", "run", "app.py"]