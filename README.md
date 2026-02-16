# Secure MCP Agent Workflow Orchestrator

A powerful, asynchronous workflow orchestration system built with Python, FastAPI, and Redis. This system allows you to define complex workflows triggered via webhooks and executed by background workers.

## 🚀 Features

- **Asynchronous Execution**: Decoupled API and Worker using Redis as an event bus.
- **Workflow Snapshots**: Persistence of execution state after specific steps for audit and recovery.
- **Dynamic Steps**: Supports HTTP requests and placeholder for MCP (Model Context Protocol) tools.
- **State Management**: Real-time run state stored in Redis with 24h TTL.
- **Database Persistence**: Permanent storage of workflow definitions and run history in PostgreSQL.

## 🛠 Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL (SQLAlchemy 2.0 + Alembic)
- **Cache/Messaging**: Redis
- **Dependency Management**: Poetry
- **Infrastructure**: Docker & Docker Compose

## 📁 Project Structure

```text
├── apps/
│   ├── api/          # FastAPI REST API
│   └── worker/       # Background execution engine
├── shared/           # Common Pydantic models and schemas
├── infra/            # Docker configuration for Postgres/Redis
└── tests/            # Integration and unit tests
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+
- `pip install poetry`

### 2. Install Dependencies
```bash
make install
```

### 3. Start Infrastructure
```bash
docker-compose up -d
```

### 4. Run the Application
You will need two separate terminal windows:

**Terminal 1 (API):**
```bash
make run-api
```

**Terminal 2 (Worker):**
```bash
make run-worker
```

## 📖 Usage Guide

### 1. Create a Workflow
Define a workflow with multiple steps (e.g., an HTTP GET followed by a state snapshot).
```bash
curl -X POST http://localhost:8000/workflows/ \
-H "Content-Type: application/json" \
-d '{
  "name": "Data Fetcher",
  "definition": {
    "version": "1.0",
    "steps": [
      {
        "type": "http",
        "method": "GET",
        "url": "https://httpbin.org/get",
        "timeout_seconds": 10
      },
      { "type": "persist_snapshot" }
    ]
  }
}'
```

### 2. Register a Webhook
Connect your workflow to a public path.
```bash
curl -X POST http://localhost:8000/workflows/<WORKFLOW_ID>/webhook-endpoints \
-H "Content-Type: application/json" \
-d '{"path": "fetch-data", "secret": "super-secret-key"}'
```

### 3. Trigger Execution
```bash
curl -X POST http://localhost:8000/webhooks/fetch-data \
-H "x-webhook-secret: super-secret-key"
```

### 4. Monitor Status
Access the interactive API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

## 🧪 Testing
Run the integration test suite:
```bash
make test
```

## 🔒 Security
- Webhooks are protected by a shared secret header (`x-webhook-secret`).
- Environment variables are managed via `.env` file.
- State snapshots ensure data persistence even if the worker restarts.
