# Sikar Cargo Transport

Fleet management and invoicing application for Sikar Cargo Transport — By Heavy & Light Trucks L.L.C.

## Features

- **Trip Management** — Record, track, and manage delivery trips
- **Invoice Generation** — Create professional PDF invoices (multiple templates)
- **Company Management** — Manage client companies and contacts
- **Driver Management** — Track drivers and cash handovers
- **Dashboard & Reports** — Real-time operational insights

## Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + SQLAlchemy + SQLite/PostgreSQL

## Development

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend
cd ..
uv run uvicorn src.main:app --reload --port 8000
```

## Production Build

```bash
cd frontend
npm run build
```

The production bundle is output to `frontend/dist/`.
