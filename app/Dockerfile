# Minimal Debian container with NGINX and UWSGI

# Use the official Debian slim image
FROM debian:bookworm-slim

# Install NGINX and UWSGI
RUN apt-get update && apt-get install -y \
    python3-pip

# Create /app/
RUN mkdir /app/

# Copy requirements.txt
COPY requirements.txt /app/

# Copy the UWSGI application
COPY main.py /app/

# Install the Python dependencies
RUN pip3 install -r /app/requirements.txt

# Expose the port
EXPOSE 8080

# Run Gunicorn
CMD gunicorn --bind 0.0.0.0:8080 main:app
