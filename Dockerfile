# MediGraph AI - Multi-stage Dockerfile

# Stage 1: Backend
FROM python:3.12-slim AS backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY mcp_server/ ./mcp_server/
COPY langgraph.json .
COPY .env.example .env

RUN mkdir -p data logs reports data/checkpoints

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "backend.app.api:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 2: Frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 3: Production
FROM python:3.12-slim AS production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    nginx \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY mcp_server/ ./mcp_server/
COPY langgraph.json .
COPY .env.example .env

COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

RUN mkdir -p data logs reports data/checkpoints

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000 8100

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

CMD ["sh", "-c", "uvicorn mcp_server.server:app --host 0.0.0.0 --port 8100 & uvicorn backend.app.api:app --host 0.0.0.0 --port 8000"]
