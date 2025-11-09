FROM python:3.12-slim

WORKDIR /app

# uv installieren
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Packages mit uv installieren
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . .
EXPOSE 8501
ENV PYTHONUNBUFFERED=1
CMD ["streamlit", "run", "streamlit/1_🗨️_Chat.py"]