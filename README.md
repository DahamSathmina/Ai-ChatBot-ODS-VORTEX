# VORTEX Ai ChatBot. Experience power of Ai.

![project-badge](https://img.shields.io/badge/project-AI--ChatBot--ODS--VORTEX-blue) ![license](https://github.com/DahamSathmina/Ai-ChatBot-ODS-VORTEX/blob/45f213f77112721e7a00fa091e65adee67726568/LICENSE) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![node](https://img.shields.io/badge/node-18%2B-green)

**Production-ready** AI Chatbot platform with a Python backend and a React + TypeScript (Vite) frontend. Designed for maintainability, observability, security, and horizontal scalability.

---

## Table of Contents

- [About](#about)
- [Status](#status)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Environment Setup (Backend)](#environment-setup-backend)
  - [Environment Setup (Frontend)](#environment-setup-frontend)
  - [Run Locally (Dev)](#run-locally-dev)
- [Production Deployment](#production-deployment)
  - [Build & Serve Frontend](#build--serve-frontend)
  - [Backend Production Serve](#backend-production-serve)
  - [Reverse Proxy & TLS (NGINX + Let's Encrypt)](#reverse-proxy--tls-nginx--lets-encrypt)
  - [Containerized Deployment (Docker Compose example)](#containerized-deployment-docker-compose-example)
  - [Kubernetes & Autoscaling (recommendation)](#kubernetes--autoscaling-recommendation)
- [API Reference (Example)](#api-reference-example)
- [Realtime & Streaming (WebSocket)](#realtime--streaming-websocket)
- [CI / CD (GitHub Actions example)](#ci--cd-github-actions-example)
- [Observability & Monitoring](#observability--monitoring)
- [Security & Secrets Management](#security--secrets-management)
- [Testing Strategy](#testing-strategy)
- [Code Style & Linting](#code-style--linting)
- [Release & Versioning](#release--versioning)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Maintainers / Contact](#maintainers--contact)
- [Acknowledgements](#acknowledgements)
- [Changelog](#changelog)

---

## About

AI-ChatBot-ODS-VORTEX is a modular platform meant to make it easy to run, improve, and operate an AI-driven conversational assistant. It provides:

- Clear separation between backend (AI orchestration, session management, security) and frontend (rich chat UI).
- Extensibility to swap LLM providers (OpenAI, Azure, Ollama, local runtime).
- Production-grade deployment guidance: containerization, CI/CD, observability, and scaling.

---

## Status

**Production-ready template (alpha)** — core patterns included. Not every optional integration (Sentry, Prometheus, Kubernetes manifests) is included by default but example snippets and best-practice guidance are provided.

---

## Technology Stack

- **Backend**: Python 3.10+ (FastAPI recommended), Uvicorn, HTTPX
- **Frontend**: React (TypeScript), Vite, Tailwind CSS
- **Containerization**: Docker, docker-compose
- **CI/CD**: GitHub Actions (example workflows included)
- **Observability**: Prometheus, Grafana, Sentry (optional)
- **Deployment options**: Docker, VPS (systemd + Nginx), Kubernetes

---

## Architecture

```
User Browser (React UI)
      │
      ├── REST / WebSocket
      │
Load Balancer / Nginx (TLS, caching, gzip)
      │
Docker / Kubernetes → Backend (FastAPI/Uvicorn)
      ├── Local caching (Redis)
      ├── Session DB (Postgres)
      └── AI Provider connector (OpenAI / Ollama / local)
```

Key principles:
- Backend is stateless where possible; use Redis/Postgres for shared state.
- Prefer streaming responses (WebSocket / Server-Sent Events) for better UX with large LLM outputs.
- Keep secrets in environment variables / secret manager.

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (recommended for parity with production)
- Git

### Environment Setup (Backend)

```bash
cd backend
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edit .env (API keys, ports, etc.)
```

Example `.env` (backend/.env):

```
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
API_PORT=8000
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost:5432/ods_db
ALLOW_ORIGINS=http://localhost:5173
```

> **Important:** Do not commit `.env`. Use GitHub Secrets (CI) or a cloud secret manager for production.

### Environment Setup (Frontend)

```bash
cd frontend
npm ci
# or `yarn`
cp .env.example .env
# Edit VITE_API_BASE and other client settings
```

Example `frontend/.env` (Vite):

```
VITE_API_BASE=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

### Run Locally (Dev)

Open two terminals.

Terminal 1 — Backend (FastAPI example):
```bash
cd backend
source .venv/bin/activate
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 — Frontend:
```bash
cd frontend
npm run dev
# default open at http://localhost:5173
```

---

## Production Deployment

### Build & Serve Frontend

```bash
cd frontend
npm run build
# serve `frontend/dist` via a static server, CDN, or Nginx
```

### Backend Production Serve

Use Uvicorn/Gunicorn with workers, or container images:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

Or run via Gunicorn with Uvicorn workers:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app:app --workers 4 --bind 0.0.0.0:8000
```

### Reverse Proxy & TLS (NGINX + Let's Encrypt)

- Use NGINX to terminate TLS, enable gzip, set caching headers, and proxy `/api` to backend.
- Use Certbot for Let's Encrypt certificates.
- Ensure `X-Forwarded-*` headers are passed to the backend.

### Containerized Deployment (Docker Compose example)

Example `docker-compose.yml` (production-ish):

```yaml
version: "3.8"
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ods
      POSTGRES_PASSWORD: ods_pass
      POSTGRES_DB: ods_db
    volumes:
      - pgdata:/var/lib/postgresql/data
  backend:
    build: ./backend
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    restart: unless-stopped
volumes:
  pgdata:
```

Adjust for production: remove volumes that expose secrets, use managed DB, and set replicas in orchestrator.

### Kubernetes & Autoscaling (recommendation)

For production scale, deploy backend to Kubernetes with Horizontal Pod Autoscaler (HPA), use managed Postgres/Redis, and put Ingress controller (NGINX/Traefik) in front. Use readiness/liveness probes and configure resource requests/limits.

---

## API Reference (example)

### POST `/api/chat`
Send a user message and receive a response.

Request:
```json
{
  "session_id": "string",
  "message": "What's the weather?",
  "metadata": { "lang": "en" }
}
```

Response:
```json
{
  "session_id": "string",
  "reply": "It's sunny in Colombo today.",
  "tokens_used": 123
}
```

### GET `/api/history?session_id=...`
Returns recent messages for the session.

### POST `/api/reset`
Reset server-side session context.

---

## Realtime & Streaming (WebSocket)

For streaming LLM output, prefer WebSocket or Server-Sent Events (SSE). Example:

Client:
```js
const ws = new WebSocket('ws://localhost:8000/ws/chat?session_id=abc');
ws.onopen = () => ws.send(JSON.stringify({ type: 'message', data: 'Hello' }));
ws.onmessage = (ev) => {
  const chunk = JSON.parse(ev.data);
  // render chunk progressively
};
```

---

## CI / CD (GitHub Actions example)

Create `.github/workflows/ci.yml` containing jobs to lint, test, and build both backend and frontend. Example steps:

- Checkout code
- Setup Python, Install backend requirements, run tests
- Setup Node, Install dependencies, build frontend, run tests
- Optionally build and push Docker images to registry (GitHub Container Registry / Docker Hub)

Store secrets (API keys) in GitHub repo Settings → Secrets.

---

## Observability & Monitoring

- **Metrics**: Expose Prometheus metrics from the backend (use `prometheus_client` for Python).
- **Tracing**: Consider OpenTelemetry for distributed tracing.
- **Logging**: Structured JSON logs (use `structlog` or `python-json-logger`) and ship to ELK / Loki.
- **Error Tracking**: Sentry for capturing exceptions in backend and frontend (Sentry SDK).
- **Health Checks**: `/health` endpoint, readiness and liveness probes for Kubernetes.

---

## Security & Secrets Management

- Do **not** store secrets in the repository.
- Use environment variables, HashiCorp Vault, AWS Secrets Manager, or GitHub Actions secrets.
- Rate-limit user inputs to avoid abuse and protect the provider's token usage.
- Validate and sanitize all user input (metadata, files).
- Apply Content Security Policy (CSP) headers for the frontend.
- Use HTTPS everywhere; enforce HSTS.

---

## Testing Strategy

- **Unit tests**: `pytest` for backend, `vitest` or `jest` for frontend.
- **Integration tests**: spinning up test database and Redis using Docker Compose.
- **E2E tests**: Playwright or Cypress for UI flows.
- **Static analysis**: `mypy` (Python), `eslint` (TS), `prettier`.

---

## Code Style & Linting

- Python: `black`, `isort`, `flake8`, `mypy`
- Frontend: `eslint` + `prettier`, `typescript`
- Enforce via Git pre-commit hooks (`pre-commit` tool) and CI pipelines.

---

## Release & Versioning

- Follow **Semantic Versioning**: `MAJOR.MINOR.PATCH`.
- Tag releases on GitHub and maintain `CHANGELOG.md`.
- Use GitHub Releases and attach build artifacts (Docker images, release notes).

---

## Troubleshooting

- CORS issues: ensure backend CORS allows the frontend origin or use a proxy.
- "Chunked" responses not arriving: confirm WebSocket proxy (NGINX) is configured to allow WebSockets.
- Rate limits / 429 errors: implement exponential backoff and circuit breaker around AI provider calls.
- Token/Quota errors: monitor usage and set alerts; implement fallback (smaller models) if quota exhausted.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Write tests and documentation for new features.
4. Create a Pull Request describing the change.
5. Maintain a clean commit history and reference issues.

Please abide by the project's Code of Conduct (Contributor Covenant).

---

## License

This repository is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See the `LICENSE` file for the full license text.

Short summary:
- You are free to use, modify, and distribute this software.
- Derivative works must also be distributed under GPL-3.0.
- Include the original copyright and license notices when redistributing.

---

## Maintainers / Contact

- **Daham Sathmina** — GitHub: https://github.com/DahamSathmina
- For bug reports and feature requests, please open an issue on the repository.

---

## Acknowledgements

- OpenAI, Ollama, and other LLM research and tooling.
- FastAPI, Uvicorn, React, Vite, Tailwind CSS for the stack inspiration.

---

## Changelog

Maintain a `CHANGELOG.md` and follow keep-a-changelog conventions.

---

**Need further customization (e.g., CI that deploys to a cloud provider, full k8s manifests, or prefilled Docker images)?** Reply with what you'd like added and I'll update the files.
