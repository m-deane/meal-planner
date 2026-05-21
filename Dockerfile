# Stage 1: Build React frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
ENV VITE_API_BASE_URL=""
RUN npm run build

# Stage 2: Python backend + serve frontend
FROM python:3.10-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source and seed script
COPY src/ ./src/
COPY scripts/seed_db.py ./scripts/seed_db.py
COPY data/seed.sql ./data/seed.sql

# Create minimal .env (env vars below override; avoids .env.example parse issues)
RUN touch .env

# Copy pre-built frontend
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p data logs meal_plans

# Configure for Hugging Face Spaces
ENV DATABASE_URL=sqlite:////app/data/recipes.db
ENV API_HOST=0.0.0.0
ENV API_PORT=7860
ENV API_DEBUG=true
ENV LOG_LEVEL=INFO
ENV LOG_FILE=""
ENV JWT_SECRET="hf-spaces-demo-key-not-for-production-use-change-me"

EXPOSE 7860

# Initialise schema, seed recipes, then start the API
CMD ["sh", "-c", "python -m src.cli init-db && python scripts/seed_db.py && uvicorn src.api.main:app --host 0.0.0.0 --port 7860"]
