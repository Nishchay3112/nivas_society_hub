# Society Hub: deployment

## Run locally
Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload` (SQLite, seeds itself on first start; API docs at :8000/docs).
Tests: `cd backend && pytest`.
Frontend: `cd frontend && npm install && npm run dev` (http://localhost:5173).

## Deploy
Frontend on Vercel/Netlify (build `npm run build`, output `dist`). Backend on Render (build `pip install -r requirements-prod.txt`, start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`) with Neon Postgres. Free backends cold-start; open /health first.

## Environment variables (names only)
Backend: `DATABASE_URL`, `JWT_SECRET`, `DEMO_MODE` (1 shows OTP on screen since SMS is mocked), `ALLOWED_ORIGIN`. Frontend: `VITE_API_URL`.

## Demo logins (OTP appears on screen)
Resident 9000000001 (paid), 9000000002 (47 days overdue, open leak), 9000000003 (partial). Help desk 9000000010. Committee 9000000020. Gate guard 9000000030 (tablet screen).
Bank demo: upload `backend/sample_bank.csv` as help desk.

If you pulled an older version, delete `backend/society.db` once so the new tables are created and reseeded.