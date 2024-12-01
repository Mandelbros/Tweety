# Use a Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy server code to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the server port (adjust to your server's port)
EXPOSE 8000

# Command to run the server
CMD ["python", "server.py"]
