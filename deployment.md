# Nivas — Deployment & Setup Guide

## 1. Deployment Status

Nivas is currently configured for local execution and has not been deployed to a public hosting environment.

This document provides instructions for setting up and running the application locally, configuring its environment variables, and accessing the demonstration accounts.

The application consists of:
- Frontend: React application.
- Backend: Python FastAPI REST API.
- Database: SQLite using SQLAlchemy.
- AI Integration: Groq API through LangChain, with Pydantic structured output for complaint classification.

---

## 2. Prerequisites

Ensure the following are installed:

- Python 3.10 or later
- Node.js and npm
- pip
- Git

A Groq API key is required for LLM-based complaint classification. The application retains rule-based classification as a fallback when the AI service is unavailable or not configured.

---

## 3. Repository Setup

Clone the public GitHub repository:

```bash
git clone https://github.com/Nishchay3112/nivas_society_hub.git
cd nivas_society_hub
```

The following instructions assume the repository contains:

```text
Nivas/
├── backend/
└── frontend/
```

---

## 4. Backend Setup

### Step 1: Navigate to the backend

```bash
cd backend
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it.

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file inside the `backend/` directory.

```env
JWT_SECRET=your_secret_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

The following optional configuration can also be specified:

```env
DATABASE_URL=sqlite:///./society.db
DEMO_MODE=1
```

Environment variable reference

| Variable | Description |
|---|---|
| `JWT_SECRET` | Secret used for signing and verifying JWT authentication tokens. |
| `GROQ_API_KEY` | API key used to access the Groq LLM service. |
| `GROQ_MODEL` | Groq model used for complaint classification. Defaults to `openai/gpt-oss-20b`. |
| `DATABASE_URL` | Optional database connection string. Defaults to local SQLite when omitted. |
| `DEMO_MODE` | Enables the demonstration OTP flow. Defaults to enabled in the backend. |

Use a stable `JWT_SECRET` so existing authentication tokens remain valid across backend restarts.

Never commit the `.env` file or expose actual credentials in the repository.

### Step 5: Start the backend

From the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

The backend creates database tables and initializes synthetic sample data during application startup when the database is empty.

### Step 6: Run backend tests

From the `backend/` directory:

```bash
pytest
```

---

## 5. Frontend Setup

Open a separate terminal.

### Step 1: Navigate to the frontend

```bash
cd frontend
```

### Step 2: Install dependencies

```bash
npm install
```

### Step 3: Configure the backend API URL

If the frontend uses `VITE_API_URL` for backend configuration, create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Step 4: Start the development server

```bash
npm run dev
```

The frontend will be available at:

```text
http://localhost:5173
```

Ensure the frontend is configured to communicate with the running backend.

---

## 6. Database and Sample Data

Nivas uses SQLAlchemy for database operations.

By default, the backend uses a local SQLite database:

```text
backend/society.db
```

Database tables are created automatically during application startup.

The seed routine initializes synthetic demonstration data, including:

- Resident and staff accounts.
- Residential flat records.
- Maintenance bills and payment records.
- Sample complaints.
- Society notices.
- Visitor records.
- Amenity bookings.

The seed routine skips initialization if flat records already exist.

Resetting the local database

If an older database does not contain newly introduced tables or you want to regenerate the sample dataset:

1. Stop the backend.
2. Back up any data you need.
3. Delete `backend/society.db`.
4. Restart the backend.

The database will be recreated and the seed routine will initialize the sample data.

---

## 7. Demo Login Credentials

The application supports demonstration authentication through OTP.

When `DEMO_MODE=1`, the OTP is displayed through the backend's test-mode authentication flow instead of being sent through an SMS provider.

Use the following synthetic demonstration accounts:

| Role | Phone Number | Demonstration Scenario |
|---|---|---|
| Resident | `9000000001` | Maintenance paid |
| Resident | `9000000002` | 47 days overdue; open leakage complaint |
| Resident | `9000000003` | Partial payment |
| Helpdesk | `9000000010` | Complaint management and bank reconciliation |
| Committee | `9000000020` | Committee dashboard |
| Gate Guard | `9000000030` | Security and visitor management |

The OTP required for login is displayed in the demonstration flow.

These accounts use synthetic sample data and are intended only for application demonstration.

### Bank Reconciliation Demo

To demonstrate bank transaction reconciliation:

1. Log in using the helpdesk account.
2. Navigate to the bank reconciliation section.
3. Upload the sample CSV file:

```text
backend/sample_bank.csv
```

The system attempts deterministic matching using transaction references, UPI information, and payment amounts.

Unambiguous matches can be automatically allocated. Ambiguous transactions are retained for manual review.

---

## 8. AI Complaint Triage

Nivas includes an AI-assisted complaint classification workflow.

When a resident submits a complaint:

1. The backend first evaluates the complaint using deterministic classification rules.
2. Safety-related keywords trigger immediate escalation through the rule-based path.
3. For other complaints, the backend invokes the configured Groq LLM when available.
4. The model returns structured classification output validated using Pydantic.
5. Low-confidence classifications are routed to manual triage.
6. The resulting category and urgency are used in the complaint assignment workflow.

Fallback and safety handling

- If `GROQ_API_KEY` is missing, rule-based classification is used.
- If the LLM request fails, the backend falls back to the deterministic result.
- Safety-related complaints are escalated without waiting for the LLM.
- The LLM cannot downgrade urgency already established by deterministic rules.

The confidence score is a classification score and should not be interpreted as a calibrated probability.

---

## 9. Important Limitations

- The application is not currently deployed to a public hosting environment.
- Maintenance payments use a demonstration flow; no real payment gateway is integrated.
- OTP delivery is mocked; no production SMS provider is configured.
- AI-based classification requires a valid Groq API key and network connectivity.
- Rule-based classification provides fallback behavior when AI processing is unavailable.
- Bank reconciliation uses deterministic matching, with ambiguous transactions requiring manual review.
- Visitor data cleanup is triggered during application startup rather than by a scheduled background job.

---

## 10. Future Deployment Considerations

A potential deployment architecture would use:

| Component | Proposed Service |
|---|---|
| Frontend | Vercel or Netlify |
| Backend | Render |
| Database | Neon Postgres |

For a future hosted deployment:

- Build the frontend using `npm run build`.
- Use `dist` as the frontend build output directory.
- Install backend dependencies using `pip install -r requirements.txt`.
- Start FastAPI using:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The following environment variables would need to be configured:

Backend:
- `DATABASE_URL`
- `JWT_SECRET`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `DEMO_MODE`
- `ALLOWED_ORIGIN`

Frontend:
- `VITE_API_URL`

This hosting configuration is a proposed future setup and does not represent an existing deployment.

A production deployment would also require persistent database storage, production-grade OTP delivery, secure environment configuration, and appropriate access-control and CORS settings.

---

## 11. Security Notes

- Do not commit `.env` files, API keys, JWT secrets, or local database files.
- Use synthetic demonstration accounts and data.
- Keep authentication secrets stable and private.
- Replace mocked OTP delivery before production use.
- Use a persistent database for hosted environments.
- Review authentication, authorization, and CORS configuration before exposing the application publicly.