# client/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY client/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY client/ .

CMD ["streamlit", "run", "app.py"]