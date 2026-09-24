ULTIMATE DEVELOPMENT SPECIFICATION
# Real-Time-local-Information-Engine
1. PRODUCT VISION

Build a Real-Time Hyperlocal Information Engine. The product is NOT a traffic app. Traffic is only the first working demonstration.

Users mainly interact through WhatsApp. They can ask local questions or submit observations. The system should use current observations, freshness, location, user context and community reports to answer questions. If useful fresh information does not exist, the architecture must support requesting fresh verification from relevant nearby/opted-in users and then updating the answer.

Example: “Is there heavy traffic near Begumpet?”

Example: “Is the ration shop open?”

Example: “Is the road blocked?”

Example: “Is water available?”

Example: “What is happening near me?”

Long-term goal: a generic engine that can handle many categories of hyperlocal information without redesigning the core system.

2. CORE PRODUCT BEHAVIOR

User asks a question
        ↓
Understand intent + entity + location
        ↓
Check recent observations
        ↓
Fresh useful information exists?
   YES ───────────────→ Answer user
   NO
        ↓
Determine whether fresh verification is needed
        ↓
Find relevant opted-in users / sources
        ↓
Collect new observations
        ↓
Consensus + freshness
        ↓
Store updated information
        ↓
Answer original user
        ↓
If relevant and opted-in → notification

3. KEY DESIGN PRINCIPLE

The core product is the Observation Engine, not WhatsApp, traffic, or the AI model. Channels must call reusable application services. Business logic must never be trapped inside the WhatsApp webhook.

Every observation represents WHO + WHAT + WHERE + WHEN, with optional source/confidence metadata.

4. EXAMPLE OBSERVATIONS

TRAFFIC  → HEAVY      → Begumpet       → 18:30
SHOP     → OPEN        → Ration Shop X   → 10:15
ROAD     → BLOCKED     → Road Y          → 17:40
WATER    → AVAILABLE   → Village Z       → 08:00
POWER    → OUTAGE      → Area A          → 21:10

The same observation/retrieval/consensus architecture should support all categories. Do not hard-code the whole platform around traffic.

5. CORE ARCHITECTURE

Users
  ↓
WhatsApp / future Web / future Mobile / API
  ↓
Channel Adapter
  ↓
Conversation Engine
  ↓
Context Engine
  ├── location context
  ├── explicit preferences
  └── useful past interaction context
  ↓
Query / Report Understanding
  ↓
Information Retrieval Engine
  ↓
Observation Engine
  ├── freshness
  ├── deduplication
  ├── source
  └── consensus
  ↓
Answer Engine
  ├── direct answer
  └── verification request when needed
  ↓
Notification Engine
  ↓
User

6. INITIAL TECHNOLOGY STACK

Python 3.12+

FastAPI + Uvicorn

PostgreSQL / Supabase

SQLAlchemy 2.x

Alembic

Pydantic v2

httpx

pytest

Git + GitHub

Twilio WhatsApp initially

Groq/Llama only as optional language-understanding fallback

Render for initial backend deployment

Use a modular monolith initially. Do NOT start with microservices, Kafka, Kubernetes, Redis, Celery, RabbitMQ or other infrastructure unless a later measured requirement justifies it.

---

## 7. Quickstart & Local Setup

```bash
# 1. Clone repository
git clone https://github.com/EswarChittala/Real-Time-local-Information-Engine.git
cd Real-Time-local-Information-Engine

# 2. Setup virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
alembic upgrade head

# 5. Run test suite
pytest

# 6. Launch development server
uvicorn app.main:app --reload --port 8000
```

- **Health check**: `http://localhost:8000/health`
- **Swagger Docs**: `http://localhost:8000/docs`
- **Engine Summary**: `http://localhost:8000/summary`

---

## 8. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck returning status & version |
| `POST` | `/observations` | Submit a real-world observation (TRAFFIC, SHOP, ROAD, WATER, POWER) |
| `GET` | `/observations/search` | Search observations by category, location, and freshness |
| `POST` | `/questions` | Ask a hyperlocal question; retrieves observations & calculates consensus |
| `POST` | `/webhooks/whatsapp` | Twilio WhatsApp incoming webhook channel adapter |
| `POST` | `/notifications/preferences` | Set user category and location notification preferences |
| `GET` | `/notifications/user/{phone}` | View notification history for a user |
| `GET` | `/summary` | High-level engine metrics and real-time category statistics |

---

## 9. Production Deployment

### Option A: Render (1-Click Deployment)
The repository includes a `render.yaml` blueprint. Link your GitHub repository in Render to deploy automatically with Alembic migrations and zero-downtime health checks.

### Option B: Docker
```bash
docker build -t hyperlocal-engine:latest .
docker run -p 8000:8000 -e DATABASE_URL="postgresql://..." hyperlocal-engine:latest
```

