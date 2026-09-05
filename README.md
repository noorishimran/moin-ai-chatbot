# MoinSystems AI Public Website Chatbot

An AI-powered public website chatbot developed for MoinSystems AI.

The chatbot provides grounded answers about MoinSystems AI services using Retrieval-Augmented Generation (RAG), manages user sessions, detects user intent, and captures leads when a visitor shows clear commercial/high intent.

The application consists of a FastAPI backend, PostgreSQL with pgvector, a React/TypeScript frontend, Gemini-based AI services, and email notifications for qualified leads.

---

## Live Deployment

### Frontend
https://moin-ai-chatbot-navy.vercel.app/

### Backend API
https://moin-ai-chatbot-production-2cf8.up.railway.app

Deployment:

- Frontend: Vercel
- Backend: Railway
- Database: PostgreSQL + pgvector
- AI Provider: Google Gemini
- Lead Notification: Mailtrap API

---

## Main Features

### AI Website Chatbot

Visitors can ask questions about MoinSystems AI, including:

- AI development
- SaaS development
- MVP development
- AI chatbot development
- Automation services
- Other supported company/service information available in the RAG knowledge base

The chatbot generates responses using retrieved company information rather than relying only on the language model.

### Retrieval-Augmented Generation (RAG)

The backend retrieves relevant information from the MoinSystems AI knowledge base before generating supported answers.

Main RAG components include:

- Knowledge-base ingestion
- Embeddings
- PostgreSQL + pgvector
- Similarity retrieval
- Context-grounded prompting
- Configurable retrieval threshold and Top-K results

When reliable supporting information is not available, the chatbot is designed to avoid inventing unsupported company information.

### Intent Detection

The chatbot classifies user messages so different types of requests can follow the appropriate flow.

Examples include:

- General information
- Service questions
- Pricing questions
- High commercial intent
- Human handoff
- Safety-related requests

### High-Intent Lead Capture

The chatbot does not force every visitor to submit contact information.

Lead capture is triggered when the visitor shows clear commercial intent, for example:

> "I am ready to hire MoinSystems AI for an AI SaaS project and want to start development. Please contact me."

The chatbot then displays a structured lead form.

The form can collect:

- Full name
- Email address
- Contact number
- Service interest
- Optional company name
- Optional project summary
- Optional timeline
- Optional budget range
- Source page

General informational or pricing questions can be answered without automatically forcing the lead form.

### Lead Notification

After a valid lead is submitted:

1. The backend validates the submitted information.
2. The lead is stored in the database.
3. An internal notification is sent through the Mailtrap HTTP API.
4. Email delivery status is recorded.
5. The frontend displays a success or failure state based on the backend result.

The application does not intentionally display a successful email-notification state when the notification fails.

### Session Management

A new chatbot session is created when the widget loads.

The session token is used by the backend to associate requests with the appropriate conversation/session.

---

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- asyncpg
- Pydantic
- Google GenAI SDK
- HTTPX

### Frontend

- React
- TypeScript
- Vite
- CSS

### AI / RAG

- Google Gemini
- Gemini Embeddings
- PostgreSQL vector search
- Retrieval-Augmented Generation

### Infrastructure

- Railway
- Vercel
- PostgreSQL
- Mailtrap API

---

## Project Structure

```text
moin-ai-chatbot/
│
├── app/
│   ├── api/
│   │   └── v1/
│   ├── chat/
│   ├── core/
│   ├── db/
│   ├── email/
│   ├── leads/
│   ├── llm/
│   ├── rag/
│   ├── schemas/
│   └── main.py
│
├── scripts/
│   ├── create_tables.py
│   ├── ingest_rag_data.py
│   └── evaluate_retrieval.py
│
├── tests/
│   └── test_api.py
│
├── widget/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api.ts
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── main.tsx
│   │   └── types.ts
│   └── package.json
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Environment Configuration

Create a `.env` file in the project root for local development.

Example:

```env
APP_ENV=local
APP_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174

APP_SECRET=your-secret

DATABASE_URL=your-postgresql-connection-string

GEMINI_API_KEY=your-gemini-api-key
MODEL_NAME=your-gemini-model
EMBEDDING_MODEL=your-embedding-model

EMAIL_PROVIDER=mailtrap_api
MAILTRAP_API_TOKEN=your-mailtrap-api-token
MAILTRAP_SANDBOX_ID=your-mailtrap-sandbox-id
LEAD_EMAIL_TO=your-internal-email

RATE_LIMIT_PER_MINUTE=30
RAG_TOP_K=5
RAG_MIN_SIMILARITY=0.65
```

Never commit real API keys, passwords, database credentials, or other secrets to Git.

---

## Local Backend Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd moin-ai-chatbot
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create the `.env` file and configure the required local values.

### 5. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

The local API will normally be available at:

```text
http://127.0.0.1:8000
```

---

## Local Frontend Setup

Open another terminal:

```bash
cd widget
npm install
npm run dev
```

The Vite development server will display its local URL in the terminal.

The backend CORS configuration must allow the frontend origin.

---

## Production Build

To verify the frontend production build:

```bash
cd widget
npm run build
```

Latest local verification:

```text
23 modules transformed
Build completed successfully
```

---

## Testing

### Backend/API Tests

Start the local backend:

```bash
uvicorn app.main:app --reload
```

Then, from another terminal:

```bash
pytest -q
```

Latest verified result:

```text
4 passed
```

The API test suite verifies core API availability, including health/API availability, required routes, and session creation.

### Production Smoke Testing

The deployed application was manually tested through the Vercel frontend.

Verified production flow:

```text
Visitor
   ↓
Vercel Frontend
   ↓
Railway FastAPI Backend
   ↓
Intent Detection
   ↓
High-Intent Lead Form
   ↓
Lead Submission
   ↓
Database
   ↓
Mailtrap Notification
```

The final production lead test successfully:

- Loaded the deployed website
- Created/used the chatbot session
- Sent messages to the deployed backend
- Detected a clear high-intent request
- Displayed the structured lead form
- Submitted the lead successfully
- Sent the internal Mailtrap notification
- Displayed the successful notification state to the visitor

---

## Example Lead Flow

Example visitor message:

```text
I am ready to hire MoinSystems AI for an AI SaaS project and want to
start development. Please contact me.
```

Expected chatbot behavior:

```text
High intent detected
        ↓
Short response
        ↓
Lead form displayed
        ↓
Visitor submits contact/project information
        ↓
Backend validation
        ↓
Lead saved
        ↓
Internal email notification
        ↓
User-safe success/failure response
```

A normal pricing question alone does not automatically trigger the lead form.

---

## API Documentation

FastAPI automatically provides interactive API documentation while the backend is running.

Local Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

## Deployment Notes

### Backend

The backend is deployed on Railway.

Production environment variables are configured through Railway rather than committed to the repository.

### Frontend

The React/Vite frontend is deployed on Vercel using:

```text
Root Directory: widget
Framework: Vite
Build Command: npm run build
Output Directory: dist
```

### CORS

The backend allows the production Vercel frontend origin in addition to the required local development origins.

### Email Transport

Lead notifications use the Mailtrap HTTP API.

HTTP API delivery was used for the deployed environment after SMTP connectivity from the deployment environment proved unreliable.

### Deployment Platform Deviation

The original project milestone referenced Render for deployment.

Railway was used for the final backend deployment because it provided a practical deployment path for the PostgreSQL-backed application in the available environment.

The application architecture itself remains portable and is not intended to depend on Railway-specific application logic.

---

## Security Considerations

The application includes or follows the following practices:

- Environment-based secret management
- Server-side lead validation
- CORS restrictions
- Request/rate limiting configuration
- API input validation through Pydantic
- Database-backed session/lead handling
- No secrets stored in frontend source code
- No production credentials committed to the repository

`.env` must remain excluded from Git.

---

## Retrieval Evaluation Note

Retrieval evaluation was performed against the supplied RAG evaluation material.

Some older evaluation expectations contain CRM-related references. The current chatbot implementation follows the newer project requirements/SRS, where CRM functionality is outside the scope of this public chatbot project.

These older expectations should therefore not be interpreted as required CRM functionality in the final implementation.

---

## Current Deployment Status

| Component | Status |
|---|---|
| FastAPI Backend | PASS |
| PostgreSQL Database | PASS |
| pgvector / RAG | PASS |
| Gemini Integration | PASS |
| Session Creation | PASS |
| Intent Detection | PASS |
| High-Intent Lead Capture | PASS |
| Mailtrap Lead Notification | PASS |
| React/Vite Frontend | PASS |
| Frontend Production Build | PASS |
| Backend/API Tests | 4 Passed |
| Railway Deployment | PASS |
| Vercel Deployment | PASS |
| Production Lead Smoke Test | PASS |

---

## Final Handoff

The project is deployed and the main end-to-end public chatbot workflow has been verified.

Production architecture:

```text
User
  ↓
React / TypeScript Widget
  ↓
Vercel
  ↓
FastAPI REST API
  ↓
Railway
  ├── PostgreSQL + pgvector
  ├── Gemini / RAG
  ├── Session Management
  ├── Intent Detection
  └── Lead Capture
           ↓
      Mailtrap API
           ↓
   Internal Notification
```

For future deployment or maintenance:

1. Configure all required environment variables.
2. Ensure PostgreSQL and pgvector are available.
3. Run/verify the database setup and RAG ingestion process where required.
4. Deploy the FastAPI backend.
5. Configure the production frontend origin in backend CORS.
6. Configure the frontend to use the production backend.
7. Build and deploy the Vite frontend.
8. Run API, chatbot, lead-capture, and email-notification smoke tests.
9. Never expose production secrets in the repository or frontend.

---

## Project Status

**MoinSystems AI Public Website Chatbot — Deployed and operational.**