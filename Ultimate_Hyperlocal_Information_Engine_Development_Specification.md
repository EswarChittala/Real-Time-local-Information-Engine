**ULTIMATE DEVELOPMENT SPECIFICATION**

**Real-Time Hyperlocal Information Engine**

_Master document for Antigravity / Claude / DeepSeek / coding agents_

# 1\. PRODUCT VISION

Build a Real-Time Hyperlocal Information Engine. The product is NOT a traffic app. Traffic is only the first working demonstration.

Users mainly interact through WhatsApp. They can ask local questions or submit observations. The system should use current observations, freshness, location, user context and community reports to answer questions. If useful fresh information does not exist, the architecture must support requesting fresh verification from relevant nearby/opted-in users and then updating the answer.

- Example: "Is there heavy traffic near Begumpet?"
- Example: "Is the ration shop open?"
- Example: "Is the road blocked?"
- Example: "Is water available?"
- Example: "What is happening near me?"

Long-term goal: a generic engine that can handle many categories of hyperlocal information without redesigning the core system.

# 2\. CORE PRODUCT BEHAVIOR

```
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
```

# 3\. CORE ARCHITECTURE

```
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
```

# 4\. KEY DESIGN PRINCIPLE

The core product is the Observation Engine, not WhatsApp, traffic, or the AI model. Channels must call reusable application services. Business logic must never be trapped inside the WhatsApp webhook.

Every observation represents WHO + WHAT + WHERE + WHEN, with optional source/confidence metadata.

# 5\. EXAMPLE OBSERVATIONS

```
TRAFFIC  → HEAVY      → Begumpet       → 18:30
SHOP     → OPEN        → Ration Shop X   → 10:15
ROAD     → BLOCKED     → Road Y          → 17:40
WATER    → AVAILABLE   → Village Z       → 08:00
POWER    → OUTAGE      → Area A          → 21:10
```

The same observation/retrieval/consensus architecture should support all categories. Do not hard-code the whole platform around traffic.

# 6\. INITIAL TECHNOLOGY STACK

- Python 3.12+
- FastAPI + Uvicorn
- PostgreSQL / Supabase
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- httpx
- pytest
- Git + GitHub
- Twilio WhatsApp initially
- Groq/Llama only as optional language-understanding fallback
- Render for initial backend deployment

Use a modular monolith initially. Do NOT start with microservices, Kafka, Kubernetes, Redis, Celery, RabbitMQ or other infrastructure unless a later measured requirement justifies it.

# 7\. CORE MODULES

```
app/
├── main.py
├── api/routes/
│   ├── health.py
│   ├── questions.py
│   ├── observations.py
│   ├── whatsapp.py
│   └── notifications.py
├── core/
│   ├── config.py
│   ├── security.py
│   ├── logging.py
│   └── exceptions.py
├── db/
├── models/
├── schemas/
├── repositories/
├── services/
│   ├── conversation_service.py
│   ├── context_service.py
│   ├── observation_service.py
│   ├── retrieval_service.py
│   ├── consensus_service.py
│   ├── verification_service.py
│   ├── notification_service.py
│   ├── response_service.py
│   ├── location_service.py
│   ├── whatsapp_service.py
│   └── ai_service.py
├── utils/
└── tests/
```

The exact folder structure may be adjusted if the coding agent has a clear reason, but keep responsibilities separated and understandable.

# 8\. DATABASE FOUNDATION

Initial core entities:

- Users — identity, activity and privacy-safe context
- Locations — named places/areas, coordinates and aliases
- Entities — shops, roads, services, places and other subjects
- Observations — real-world reports
- Questions — user questions and parsed intent
- UserPreferences — explicit interests and notification choices
- Notifications — notification history and deduplication

Keep the schema simple enough to build now, but extensible enough for future categories. Do not create a huge generic schema that makes the MVP difficult.

# 9\. OBSERVATION MODEL

```
Observation
-----------
id
reporter_id
category
event_type / attribute
entity_id (optional)
location_id
value / state
raw_message
source
confidence (optional)
observed_at
created_at
expires_at (optional)
```

Traffic can use category=TRAFFIC and value/state=CLEAR, MODERATE, HEAVY or BLOCKED. Other categories must be able to use the same observation pipeline.

# 10\. RETRIEVAL + FRESHNESS

When a question arrives, first search existing observations. Do not immediately ask users or call an LLM.

```
Question
  ↓
Resolve category/entity/location
  ↓
Retrieve relevant observations
  ↓
Check freshness
  ↓
Enough fresh information?
  ├── Yes → aggregate → answer
  └── No  → verification workflow later
```

Freshness must be configurable by category. For the first traffic implementation, use a simple configurable window such as TRAFFIC_REPORT_MAX_AGE_MINUTES=30. Do not build complex time-decay initially.

# 11\. CONSENSUS

Use independent recent observations. Repeated reports from one person must not create multiple witnesses.

```
0 valid reports → UNKNOWN
1 independent recent report → REPORTED
2+ independent agreeing reports → CONFIRMED
Recent disagreement → CONFLICTING
```

The first traffic implementation should use this simple deterministic rule. Later versions may add distance, source reliability, reporter reputation, time decay and confidence weighting.

# 12\. USER CONTEXT

The architecture should support user context, but privacy must come first.

- Explicit notification preferences
- User-provided location when available
- Important locations selected by the user
- Previous questions/interactions that are useful for personalization
- Frequently requested categories/locations where appropriate
- Geographic relevance

Do not assume continuous GPS tracking. Do not infer sensitive personal attributes. Do not send personalized notifications without appropriate user control/opt-in.

# 13\. VERIFICATION ENGINE

When fresh information is missing, the future verification engine can request observations from relevant opted-in users.

```
User A asks
  ↓
No sufficiently fresh observation
  ↓
Find eligible nearby/relevant opted-in users
  ↓
Request verification
  ↓
Receive observations
  ↓
Consensus
  ↓
Update information
  ↓
Answer A
```

This is a future capability, but design the core interfaces so it can be added without rewriting the observation engine.

# 14\. NOTIFICATION ENGINE

Notifications are a separate subsystem. A new observation does not automatically mean every user should be notified.

```
Fresh observation
  ↓
Is it relevant?
  ↓
Did the user opt in?
  ↓
Geographic/category relevance?
  ↓
Already notified?
  ↓
Cooldown / anti-spam
  ↓
Send notification
```

Notifications should be useful, novel and controlled rather than frequent by default.

# 15\. AI / NLP

Use deterministic parsing for simple requests. Use an LLM only when language is difficult, such as Telugu-English, slang, spelling variations or ambiguous natural language.

```
User message
  ↓
Normalization
  ↓
Deterministic parser
  ├── understood → business logic
  └── not understood → optional AI
                              ↓
                         structured JSON
                              ↓
                         validation
                              ↓
                         business logic
```

AI is not the source of truth. It must never directly write to the database, invent observations, invent witnesses, bypass validation or override consensus.

# 16\. WHATSAPP

Use Twilio initially as a channel adapter. Keep Twilio-specific code inside whatsapp_service.py / webhook routes.

```
WhatsApp
  ↓
Twilio webhook
  ↓
signature validation
  ↓
Conversation Engine
  ↓
core services
  ↓
Response Engine
  ↓
Twilio
  ↓
WhatsApp
```

The same core services must later be reusable by Web, Mobile or another messaging provider.

# 17\. SECURITY

- HTTPS in production
- Validate Twilio webhook signatures
- Environment variables for secrets
- Never commit .env or credentials
- Input validation and size limits
- Rate limiting / report cooldowns
- Idempotency for webhook retries
- Safe error responses
- Privacy-safe logging
- Never log API keys, passwords or authentication tokens

# 18\. API FOUNDATION

```
GET  /health
POST /questions
POST /observations
GET  /observations/search
POST /webhooks/whatsapp
```

Add more endpoints only when required. The API should expose application capabilities, not duplicate business logic in every route.

# 19\. TESTING

- Health endpoint
- Location/entity resolution
- Question parsing
- Observation creation
- Freshness
- Duplicate handling
- Same-user repeated reports
- Two independent witnesses
- Conflicting reports
- Unknown data
- AI fallback failure
- Webhook idempotency
- Notification deduplication
- End-to-end traffic scenario

The first complete demonstration should be: User A reports heavy traffic near Begumpet → User B reports heavy traffic near Begumpet → User C asks about traffic → system retrieves recent reports → confirms two independent witnesses → answers C.

# 20\. DEVELOPMENT PHASES

```
PHASE 1  FastAPI + Git + /health
PHASE 2  PostgreSQL + core data model
PHASE 3  Generic observations + questions
PHASE 4  Retrieval + freshness + consensus
PHASE 5  Traffic as first complete category
PHASE 6  WhatsApp integration
PHASE 7  AI language fallback
PHASE 8  Verification engine
PHASE 9  User context + personalized notifications
PHASE 10 More categories + map/web interface
PHASE 11 Scaling only when actually needed
```

Do not implement all phases at once.

# 21\. DEVELOPMENT RULES FOR THE AI CODING AGENT

- Build one phase at a time.
- Explain what and why before coding.
- Give exact commands to run.
- Add tests with each meaningful feature.
- Do not generate a huge unexplained codebase.
- Do not assume advanced knowledge.
- Keep code simple and maintainable.
- Use type hints and clear names.
- Separate routes, services and persistence.
- Never hide business logic inside a WhatsApp webhook.
- Stop after each major phase and wait for my confirmation.
- If requirements are ambiguous, ask before making a major architectural assumption.
- When external APIs/services are involved, use their current official documentation.

# 22\. MVP SUCCESS CRITERIA

- A user can submit a real-world observation.
- A user can ask a question about a known local subject.
- The system can retrieve recent relevant observations.
- Freshness is respected.
- Independent witnesses are counted correctly.
- Conflicting information is represented honestly.
- The system can answer a traffic question end-to-end.
- WhatsApp can be used as the first interface.
- The core engine does not depend on AI being available.
- The architecture can add new information categories without rewriting the core.

# 23\. WHAT NOT TO BUILD FIRST

- No mobile app
- No complex map UI
- No global geocoding
- No continuous location tracking
- No predictive ML
- No complex reputation system
- No microservices
- No Kubernetes
- No Kafka
- No Redis unless needed later
- No complex agentic AI
- No large-scale analytics

# 24\. FIRST TASK — START HERE

Start Phase 1 only.

```
1. Verify Python 3.12+
2. Create project directory
3. Create virtual environment
4. Initialize Git
5. Create basic FastAPI structure
6. Install FastAPI + Uvicorn
7. Create GET /health
8. Run the server
9. Test /health
10. Make the first Git commit
```

STOP after Phase 1. Do not build the database, WhatsApp, AI, verification or notifications yet.

# 25\. GOLDEN PRINCIPLE

Build a generic hyperlocal information core, prove it with one complete real-world category, then expand. Traffic is the first use case—not the identity of the product.

The final system should be understandable, secure, modular, privacy-conscious, low-cost initially, and capable of growing into a real-time community information network.