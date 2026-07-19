# LegalFlow AI — Multi-Agent Commercial Tenancy Legal Compliance SaaS Platform

**LegalFlow AI** is an enterprise-grade AI-powered legal workflow automation platform engineered specifically for **Commercial Tenancy Management in Sri Lanka**.

It automates lease agreement compliance, rent payment monitoring, deterministic financial arrears/statutory interest calculation, RAG legal research, and human-in-the-loop legal document drafting (Payment Reminders, Statutory Notice to Quit under Act No. 1 of 2023, and Letters of Demand).

---

## 🏛️ Key System Features

- **Smart Rent Payment Monitoring**: Automated payment schedules, grace period enforcement, and gateway payment link generation.
- **Deterministic Financial Engine**: Pre-calculated monetary facts (arrears, simple statutory interest at 12% p.a., overdue days). *AI never computes numbers.*
- **LlamaIndex + LangChain Legal RAG**: Structural semantic chunking of Sri Lankan statutes (*Recovery of Possession of Premises Given on Lease Act No. 1 of 2023*, *Rent Act No. 7 of 1972*, *Civil Procedure Code*) indexed in ChromaDB.
- **LangGraph Multi-Agent AI Workflow**: 5 specialized AI agents (Lease Parser, Financial, Legal Research, Legal Analysis, Legal Drafting) orchestrated via a state machine with a Decision Router.
- **Human-in-the-Loop Approval**: All generated statutory notices require explicit landlord review and approval (`DRAFT` -> `APPROVED` / `REJECTED`).

---

## 🏗️ Architecture & Monorepo Structure

```
LegalFlow_AI/
├── backend/            # Async FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic, Clean Repositories
├── ai-service/         # Independent FastAPI + LangGraph Multi-Agent System (OpenRouter / Mistral Large)
├── rag/                # Legal RAG Pipeline (LlamaIndex TextNodes + HuggingFace + ChromaDB)
├── n8n/                # n8n Automation Workflows & Local Setup Documentation
├── docker/             # Production Dockerfiles
├── tests/              # Pytest unit & integration test suites
└── docker-compose.yml  # Multi-container orchestration
```

---

## 🚀 Quick Start Guide

### 1. Clone & Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your `OPENROUTER_API_KEY` (or `OPENAI_API_KEY`) in `.env`.

### 2. Launch Services with Docker Compose
```bash
docker-compose up --build -d
```

Service Access Points:
- **Core Backend API**: `http://localhost:8005/docs`
- **AI Microservice**: `http://localhost:8001/docs`
- **RAG Microservice**: `http://localhost:8002/docs`
- **n8n Automation Console**: `http://localhost:5678` (Login: `admin` / `admin`)
- **ChromaDB Vector Store**: `http://localhost:8000`

---

## 🧪 Running Automated Tests

```bash
# Run Financial Engine & RAG tests
pytest tests/
```

---

## 📚 API Endpoints Summary

### Authentication & Core CRUD
- `POST /api/v1/auth/register` — Register Landlord / Property Manager
- `POST /api/v1/auth/login` — Generate JWT Access Token
- `POST /api/v1/tenant` — Create Commercial Tenant
- `POST /api/v1/lease` — Register Commercial Lease Agreement

### Payments & Webhooks
- `POST /api/v1/payment` — Create Monthly Payment Item
- `POST /api/v1/payment/link` — Generate Gateway Checkout Link
- `POST /api/v1/payment/webhook` — Process Gateway Payment Notification

### AI Compliance Analysis & Human-in-the-Loop
- `POST /api/v1/analyze?case_id={id}` — Trigger LangGraph Compliance Analysis
- `GET /api/v1/documents` — View Generated Legal Documents
- `POST /api/v1/documents/{id}/approve` — Approve / Reject Notice Draft
