# syntax=docker/dockerfile:1.4

# 1. Frontend build stage
FROM node:18-alpine AS frontend-builder
WORKDIR /app
# Copy frontend package manager files
COPY frontend/package.json frontend/pnpm-lock.yaml .
# Install pnpm and dependencies
RUN npm install -g pnpm && pnpm install
# Copy the rest of the frontend source code
COPY frontend/ .
# Build the frontend
RUN pnpm run build

# 2. Final backend stage
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS final
WORKDIR /app

# Copy built frontend from the frontend-builder stage
COPY --from=frontend-builder /app/dist /app/build

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

# Copy the backend application code
COPY backend/ .

CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "main:app"]