# Production AI Agent

This is a production-ready AI Agent built with FastAPI, Docker, and Redis.

## Features
- **FastAPI Framework**: High-performance asynchronous API.
- **Dockerized**: Multi-stage Dockerfile for small image size (< 300MB).
- **Security**: API Key authentication via `X-API-Key` header.
- **Reliability**: Health and readiness checks for zero-downtime deployment.
- **Scaling**: Stateless design with Redis for horizontal scaling.
- **Guardrails**:
  - Rate limiting (10 requests/minute per user).
  - Cost guarding (Budgeting logic implemented).

## Local Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Test the API:
   ```bash
   curl -X POST http://localhost:8000/ask \
     -H "X-API-Key: tonhi-agent-day12" \
     -d '{"question": "Hello Agent"}'
   ```

## Cloud Deployment
Deployed on **Railway**.
URL: `https://2a202600369-hothitonhi-production.up.railway.app`
