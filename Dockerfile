FROM python:3.12

WORKDIR /app

# System-Dependencies für pandas/numpy
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Requirements kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Container läuft dauerhaft
CMD ["sleep", "infinity"]