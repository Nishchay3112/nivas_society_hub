# Workspace Memory
This file is maintained automatically by Code Janitor so Claude, Codex, Bob, and any other AI agent can reuse repo context without rescanning everything from scratch.
Generated: 2026-11-09T16:59:03.092Z
Workspace: resident_project
Workspace root: c:\Users\Nishchay\OneDrive\Desktop\resident_project
Refresh reason: tracked-change
Output path: graphify-out/WORKSPACE_MEMORY.md
Shared mirror: workspacememory.md
Structured manifest: workspace.json
## Handoff Guidance
- Read `graphify-out/GRAPH_REPORT.md` first when the request is about architecture, dependencies, file ownership, or codebase navigation.
- Use this memory file and the workspace-root `workspacememory.md` mirror for recent activity, hot files, Git-aware status, and GitHub-enriched project context.
- Use the workspace-root `workspace.json` file when an AI agent wants machine-readable repo metadata, file inventory, package details, and Git/Graphify summaries without rescanning the repository.
- Refresh this file with the `Code Janitor: Refresh Workspace Memory` command after significant edits or branch changes.
## Repository Blueprint
- Audience: any AI agent working in this repository can treat this file as the current handoff ledger.
- Graphify report: not available yet
- Graphify graph: not available yet
- Last activity: 2026-11-09T16:59:01.215Z
## Workspace Focus
- Active file in focus: deployment.md
- Hottest files right now: frontend/src/styles.css (22), frontend/src/App.jsx (14), backend/app/main.py (2), backend/tests/test_api.py (1)
- Suggested starting points: deployment.md, frontend/src/styles.css, frontend/src/App.jsx, backend/app/main.py, backend/tests/test_api.py, .gitignore
## Current Workspace
- Active file: deployment.md
- Tracked files in snapshot: 32
- Top-level areas: backend (19), frontend (9), [root] (4)
- Primary file types: .py (7), [no extension] (6), .json (4), .jsx (3), .md (3), .txt (2), .css (1), .csv (1)
- Key files: .gitignore, backend/.gitignore, backend/.pytest_cache/.gitignore, backend/.pytest_cache/README.md, frontend/package-lock.json, frontend/package.json
## Package Snapshot
- Package metadata unavailable: package.json was not found.
## Current Stack
- Logged change events: 40
- Change mix: save (40)
- Remembered file snapshots: 5
- Working tree summary: fatal: not a git repository (or any of the parent directories): .git
## Tracked Snapshots
- deployment.md | 18 lines | 1185 chars | hash be82c3a2fcba
  Last snapshot: 2026-11-09T16:59:01.215Z
  Preview: "# Society Hub: deployment / ## Run locally / Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload` (SQLite, seeds itself on firs..."
- backend/app/main.py | 250 lines | 13705 chars | hash 3bf31256bbc7
  Last snapshot: 2026-11-09T11:54:21.025Z
  Preview: "import os, csv, io, json, hmac, hashlib, base64, time, secrets, random / from datetime import date, datetime, timedelta / from fastapi import FastAPI, Depends, HTTPException, UploadFile, File / from fastapi.middleware..."
- backend/tests/test_api.py | 64 lines | 3904 chars | hash 433c3491c149
  Last snapshot: 2026-11-09T11:52:38.023Z
  Preview: "import os, sys, pathlib, tempfile / from datetime import date, timedelta / os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db" / os.environ["JWT_SECRET"] = "test-secret" / os.environ["DEMO_MODE"] =..."
- frontend/src/styles.css | 155 lines | 15448 chars | hash db56418b0b5d
  Last snapshot: 2026-11-08T13:40:44.949Z
  Preview: ":root{--ink:#14202b;--mute:#5f6b7a;--line:#e4e8ec;--acc:#0f6b5a;--accs:#eaf5f2;--bad:#b3261e;--bg:#fff;--soft:#f5f7f8} / @media(prefers-color-scheme:dark){:root{--ink:#edf1f4;--mute:#9aa7b4;--line:#27323c;--acc:#4fc3a..."
- frontend/src/App.jsx | 279 lines | 26169 chars | hash 133d7a600682
  Last snapshot: 2026-11-08T13:40:30.687Z
  Preview: "import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", bo..."

## Recent Changes
### 2026-11-09T16:59:01.215Z | saved | deployment.md
- Summary: Line 18: removed 2 lines.
- Before: 19 lines | 1,186 chars | hash 848f6be687b1 | preview: "# Society Hub: deployment / ## Run locally / Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload` (SQLite, seeds itself on firs..."
- After: 18 lines | 1,185 chars | hash be82c3a2fcba | preview: "# Society Hub: deployment / ## Run locally / Backend: `cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload` (SQLite, seeds itself on firs..."

### 2026-11-09T11:54:21.025Z | saved | backend/app/main.py
- Summary: Line 121: inserted 4 lines.
- Before: 247 lines | 13,470 chars | hash e74224f29ff1 | preview: "import os, csv, io, json, hmac, hashlib, base64, time, secrets, random / from datetime import date, datetime, timedelta / from fastapi import FastAPI, Depends, HTTPException, UploadFile, File / from fastapi.middleware..."
- After: 250 lines | 13,705 chars | hash 3bf31256bbc7 | preview: "import os, csv, io, json, hmac, hashlib, base64, time, secrets, random / from datetime import date, datetime, timedelta / from fastapi import FastAPI, Depends, HTTPException, UploadFile, File / from fastapi.middleware..."
- Current fragment: "def cj(c): / d = {col.name: getattr(c, col.name) for col in c.__table__.columns if col.name != "photo"} / d = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in d..."

### 2026-11-09T11:54:18.901Z | saved | backend/app/main.py
- Summary: Line 121: removed 4 lines.
- Before: 250 lines | 13,662 chars | hash 4963ce135974 | preview: "import os, csv, io, json, hmac, hashlib, base64, time, secrets, random / from datetime import date, datetime, timedelta / from fastapi import FastAPI, Depends, HTTPException, UploadFile, File / from fastapi.middleware..."
- After: 247 lines | 13,470 chars | hash e74224f29ff1 | preview: "import os, csv, io, json, hmac, hashlib, base64, time, secrets, random / from datetime import date, datetime, timedelta / from fastapi import FastAPI, Depends, HTTPException, UploadFile, File / from fastapi.middleware..."
- Previous fragment: "def cj(c): / d = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in c.__dict__.items() if not k.startswith("_") and k != "photo"} / d["has_photo"] = bool(c.photo)..."

### 2026-11-09T11:52:38.023Z | saved | backend/tests/test_api.py
- Summary: Line 26: replaced 1 line with 2 lines.
- Before: 63 lines | 3,904 chars | hash be8892af7cdb | preview: "import os, sys, pathlib, tempfile / from datetime import date, timedelta / os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db" / os.environ["JWT_SECRET"] = "test-secret" / os.environ["DEMO_MODE"] =..."
- After: 64 lines | 3,904 chars | hash 433c3491c149 | preview: "import os, sys, pathlib, tempfile / from datetime import date, timedelta / os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db" / os.environ["JWT_SECRET"] = "test-secret" / os.environ["DEMO_MODE"] =..."
- Previous fragment: "01"}); assert c.post("/auth/verify", json={"phone": "9000000001", "otp": "000000"}).status_code in (400,)"
- Current fragment: "20"}) / assert c.post("/auth/verify", json={"phone": "9000000020", "otp": "000000"}).status_code == 400"

### 2026-11-08T13:40:44.949Z | saved | frontend/src/styles.css
- Summary: Line 153: inserted 3 lines.
- Before: 153 lines | 15,400 chars | hash 17d9ca86357e | preview: ":root{--ink:#14202b;--mute:#5f6b7a;--line:#e4e8ec;--acc:#0f6b5a;--accs:#eaf5f2;--bad:#b3261e;--bg:#fff;--soft:#f5f7f8} / @media(prefers-color-scheme:dark){:root{--ink:#edf1f4;--mute:#9aa7b4;--line:#27323c;--acc:#4fc3a..."
- After: 155 lines | 15,448 chars | hash db56418b0b5d | preview: ":root{--ink:#14202b;--mute:#5f6b7a;--line:#e4e8ec;--acc:#0f6b5a;--accs:#eaf5f2;--bad:#b3261e;--bg:#fff;--soft:#f5f7f8} / @media(prefers-color-scheme:dark){:root{--ink:#edf1f4;--mute:#9aa7b4;--line:#27323c;--acc:#4fc3a..."
- Current fragment: ".lp-stats b{font-variant-numeric:tabular-nums}"

### 2026-11-08T13:40:30.687Z | saved | frontend/src/App.jsx
- Summary: Line 74: replaced 1 line with 1 line.
- Before: 279 lines | 26,166 chars | hash b3af5ad767ce | preview: "import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", bo..."
- After: 279 lines | 26,169 chars | hash 133d7a600682 | preview: "import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", bo..."
- Previous fragment: ""2,400", "homes"], ["28", "towers"], ["3", "languages"], ["1", "app for everything"]].map(([n, l]) => <div key={l}><b>{n}"
- Current fragment: "2400, "homes"], [28, "towers"], [180, "on-site staff"], [3, "languages"]].map(([n, l]) => <div key={l}><b><CountUp to={n} />"

### 2026-11-08T13:39:55.592Z | saved | frontend/src/App.jsx
- Summary: Line 19: inserted 25 lines.
- Before: 255 lines | 25,285 chars | hash 09d78cd1cd02 | preview: "import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", bo..."
- After: 279 lines | 26,166 chars | hash b3af5ad767ce | preview: "import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", bo..."
- Current fragment: "function CountUp({ to, ms = 1400 }) { / const ref = useRef(null), [n, setN] = useState(0); / useEffect(() => { / const el = ref.current; / if (!el) return; / if (window.matchMed..."

### 2026-11-08T13:39:39.374Z | saved | frontend/src/App.jsx
- Summary: Line 1: removed 2 lines.
- Before: 256 lines | 25,330 chars | hash 8f3621181b75 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home",..."
- After: 255 lines | 25,285 chars | hash 09d78cd1cd02 | preview: "import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", bo..."
- Previous fragment: "useState, useEffect } from "react"; / import {"

### 2026-11-08T13:39:34.226Z | saved | frontend/src/App.jsx
- Summary: Line 3: inserted 2 lines.
- Before: 255 lines | 25,277 chars | hash ad4891bcb0b9 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- After: 256 lines | 25,330 chars | hash 8f3621181b75 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / import { useState, useEffect, useRef } from "react"; / const L = { / en: { home: "Home",..."
- Current fragment: "import { useState, useEffect, useRef } from "react";"

### 2026-11-08T13:36:09.389Z | saved | frontend/src/App.jsx
- Summary: Line 39: removed 1 line.
- Before: 255 lines | 25,338 chars | hash a77eecc39822 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- After: 255 lines | 25,277 chars | hash ad4891bcb0b9 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- Previous fragment: "a className="lp-ghost" href="#features">See what it does</a><"

### 2026-11-08T13:34:28.175Z | saved | frontend/src/styles.css
- Summary: Line 114: inserted 40 lines.
- Before: 114 lines | 11,549 chars | hash b23aee493178 | preview: ":root{--ink:#14202b;--mute:#5f6b7a;--line:#e4e8ec;--acc:#0f6b5a;--accs:#eaf5f2;--bad:#b3261e;--bg:#fff;--soft:#f5f7f8} / @media(prefers-color-scheme:dark){:root{--ink:#edf1f4;--mute:#9aa7b4;--line:#27323c;--acc:#4fc3a..."
- After: 153 lines | 15,400 chars | hash 17d9ca86357e | preview: ":root{--ink:#14202b;--mute:#5f6b7a;--line:#e4e8ec;--acc:#0f6b5a;--accs:#eaf5f2;--bad:#b3261e;--bg:#fff;--soft:#f5f7f8} / @media(prefers-color-scheme:dark){:root{--ink:#edf1f4;--mute:#9aa7b4;--line:#27323c;--acc:#4fc3a..."
- Current fragment: "/* ===== landing page ===== */ / html{scroll-behavior:smooth} / .lp section[id]{scroll-margin-top:80px} / .lp-wrap{max-width:1120px;margin:0 auto;padding:0 24px} / .lp-nav{posit..."

### 2026-11-08T13:34:19.699Z | saved | frontend/src/styles.css
- Summary: Line 112: inserted 3 lines.
- Before: 112 lines | 11,547 chars | hash e4f7269a968a | preview: ":root{--ink:#14202b;--mute:#5f6b7a;--line:#e4e8ec;--acc:#0f6b5a;--accs:#eaf5f2;--bad:#b3261e;--bg:#fff;--soft:#f5f7f8} / @media(prefers-color-scheme:dark){:root{--ink:#edf1f4;--mute:#9aa7b4;--line:#27323c;--acc:#4fc3a..."
- After: 114 lines | 11,549 chars | hash b23aee493178 | preview: ":root{--ink:#14202b;--mute:#5f6b7a;--line:#e4e8ec;--acc:#0f6b5a;--accs:#eaf5f2;--bad:#b3261e;--bg:#fff;--soft:#f5f7f8} / @media(prefers-color-scheme:dark){:root{--ink:#edf1f4;--mute:#9aa7b4;--line:#27323c;--acc:#4fc3a..."

### 2026-11-08T13:34:13.225Z | saved | frontend/src/App.jsx
- Summary: Line 21: replaced 8 lines with 47 lines.
- Before: 216 lines | 22,288 chars | hash 45f7d80605ca | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- After: 255 lines | 25,338 chars | hash a77eecc39822 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- Previous fragment: "["Pay maintenance in two taps", "See exactly what you owe, including late interest, and pay by UPI or card. Every receipt is kept."], ["Complaints that never vanish", "Report wi..."
- Current fragment: "["pay", "Pay maintenance in two taps", "See exactly what you owe, including late interest, and pay by UPI or card. Every receipt is kept in your ledger."], / ["help", "Complaint..."

### 2026-11-08T13:34:01.272Z | saved | frontend/src/App.jsx
- Summary: Line 21: replaced 41 lines with 10 lines.
- Before: 247 lines | 24,695 chars | hash 57443758a832 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- After: 216 lines | 22,288 chars | hash 45f7d80605ca | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- Previous fragment: "["pay", "Pay maintenance in two taps", "See exactly what you owe, including late interest, and pay by UPI or card. Every receipt is kept in your ledger."], / ["help", "Complaint..."
- Current fragment: "["Pay maintenance in two taps", "See exactly what you owe, including late interest, and pay by UPI or card. Every receipt is kept."], ["Complaints that never vanish", "Report wi..."

### 2026-11-08T13:33:58.854Z | saved | frontend/src/App.jsx
- Summary: Line 21: replaced 10 lines with 41 lines.
- Before: 216 lines | 22,288 chars | hash 45f7d80605ca | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- After: 247 lines | 24,695 chars | hash 57443758a832 | preview: "import { useState, useEffect } from "react"; / import { call, useLoad, State, inr, Complaints, Bank, Dash } from "./core.jsx"; / const L = { / en: { home: "Home", pay: "Pay", help: "Help", guests: "Guests", book: "Boo..."
- Previous fragment: "["Pay maintenance in two taps", "See exactly what you owe, including late interest, and pay by UPI or card. Every receipt is kept."], ["Complaints that never vanish", "Report wi..."
- Current fragment: "["pay", "Pay maintenance in two taps", "See exactly what you owe, including late interest, and pay by UPI or card. Every receipt is kept in your ledger."], / ["help", "Complaint..."


## Hot Files
- frontend/src/styles.css (22 tracked changes)
- frontend/src/App.jsx (14 tracked changes)
- backend/app/main.py (2 tracked changes)
- backend/tests/test_api.py (1 tracked changes)
- deployment.md (1 tracked changes)

## Git Snapshot
- fatal: not a git repository (or any of the parent directories): .git

## GitHub Snapshot
GitHub context unavailable: Could not determine the GitHub repository from origin remote: fatal: not a git repository (or any of the parent directories): .git

## Graphify Snapshot
Graphify report not found. Generate Graphify output if you want architecture-aware memory excerpts here.

## Project Planner
- Project planner is not configured yet. Enable it in the chat panel to generate a time-based todo list and progress rescue briefs.

## Agent Notes
- If a future task asks what changed recently, start with `Recent Changes`, `Tracked Snapshots`, `Hot Files`, and `Git Snapshot`.
- If a future task asks how the project is organized, combine this file with `graphify-out/GRAPH_REPORT.md`.
- If a future task needs repository-level context, use `Package Snapshot`, the GitHub snapshot, and the Graphify snapshot before rescanning broad parts of the repo.
