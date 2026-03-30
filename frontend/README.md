# Disaster Alert & Community Response System

> Real-time global disaster monitoring with community-driven needs and resource matching.

![Stack](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?style=flat-square&logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=flat-square&logo=typescript)
![Supabase](https://img.shields.io/badge/Supabase-realtime-green?style=flat-square&logo=supabase)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## The Problem

When disasters strike — earthquakes, wildfires, floods — the gap between people who need help and people who can provide it is not a logistics problem. It is an information problem.

Existing platforms broadcast danger but never coordinate local response. Relief organizations operate at institutional scale. There is no lightweight, open, real-time tool that lets a survivor post a geolocated need and have a nearby volunteer find it instantly.

This project addresses that gap.

---

## What It Does

- **Live global disaster map** — pulls real earthquake data from USGS and wildfire/storm/volcano data from NASA EONET every 60 seconds automatically
- **WebSocket real-time updates** — new disaster events appear on the map instantly without any page refresh, powered by Supabase Realtime
- **Interactive markers** — color-coded by severity (M5+ red, M3.5+ orange, M2.5+ yellow, natural events blue), clickable with dark popups showing magnitude and coordinates
- **Community needs board** — survivors post geolocated needs (water, food, medical, shelter, rescue)
- **Resource matching** — volunteers post available resources; the system matches them to nearby needs using a Haversine-based proximity algorithm, sorted by distance
- **Filter by type** — switch between all events, earthquakes only, or natural events only

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                             │
│         React + TypeScript + Vite + Tailwind                │
│         MapLibre GL JS + OpenFreeMap (free tiles)           │
│         Supabase JS client (Realtime WebSocket)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP + WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                       Backend                               │
│              Python FastAPI (async/ASGI)                    │
│         APScheduler — polls every 60s background            │
│         Haversine matching engine                           │
└──────┬───────────────────────────────────────┬──────────────┘
       │ httpx async                            │ supabase-py
┌──────▼──────────┐                  ┌─────────▼──────────────┐
│  External APIs  │                  │  Supabase              │
│  USGS Earthquakes│                 │  PostgreSQL database   │
│  NASA EONET     │                  │  Realtime WebSocket    │
│  (no API keys)  │                  │  Row Level Security    │
└─────────────────┘                  └────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | Python FastAPI | Async-first, auto docs, fast |
| Server | Uvicorn (ASGI) | Production-grade async server |
| Scheduler | APScheduler | Background polling without extra infra |
| HTTP client | httpx | Async HTTP, timeout handling |
| Database | Supabase (PostgreSQL) | Free tier, built-in Realtime |
| Frontend | React + TypeScript + Vite | Modern, type-safe, fast HMR |
| Styling | Tailwind CSS | Utility-first, no CSS files |
| Map | MapLibre GL JS | Open-source WebGL maps, zero cost |
| Map tiles | OpenFreeMap | No API key, no cost, OSM data |
| Realtime | Supabase Realtime | WebSocket push on DB insert |
| Data validation | Pydantic v2 | Type-safe API contracts |

**Total infrastructure cost: $0**

---

## Data Sources

| Source | Data | Update frequency | API key required |
|---|---|---|---|
| USGS Earthquake API | Global earthquakes M2.5+ | Every 60s | No |
| NASA EONET v3 | Wildfires, storms, volcanoes | Every 120s | No |

---

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 20+
- Git
- A free [Supabase](https://supabase.com) account

### 1. Clone the repository

```bash
git clone https://github.com/aounraza379/disaster-alert-system.git
cd disaster-alert-system
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

Create `backend/.env`:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

Run the database schema from `backend/schema.sql` in your Supabase SQL editor.

Start the backend:

```bash
uvicorn app.main:app --reload
```

API runs at `http://127.0.0.1:8000` — interactive docs at `/docs`.

### 3. Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://127.0.0.1:8000
```

Start the frontend:

```bash
npm run dev
```

App runs at `http://localhost:5173`.

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/health` | Server status |
| GET | `/api/earthquakes` | Fetch + save latest earthquakes |
| GET | `/api/events` | Fetch + save latest natural events |
| GET | `/api/needs` | Get all unresolved needs |
| POST | `/api/needs` | Post a new need |
| GET | `/api/resources` | Get all available resources |
| POST | `/api/resources` | Post a new resource |
| GET | `/api/match/{need_id}` | Match a need to nearby resources |

Full interactive documentation available at `/docs` when running locally.

---

## The Matching Algorithm

Needs are matched to resources using the **Haversine formula** — the standard method for calculating great-circle distance between two GPS coordinates on Earth's surface.

```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlon/2)
distance = 2R × arctan2(√a, √(1−a))
```

Where R = 6371km (Earth's mean radius). Results are filtered by a configurable radius (default 50km) and sorted closest-first. Only resources in the same category as the need are considered.

---

## Project Structure

```
disaster-alert-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── matching.py      # needs/resources/matching routes
│   │   ├── core/
│   │   │   ├── config.py        # environment variables
│   │   │   ├── database.py      # Supabase client
│   │   │   └── scheduler.py     # background polling jobs
│   │   ├── services/
│   │   │   ├── usgs.py          # USGS fetch + save
│   │   │   └── eonet.py         # NASA EONET fetch + save
│   │   └── main.py              # FastAPI app + lifespan
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DisasterMap.tsx  # MapLibre map + markers
│   │   │   └── NeedsPanel.tsx   # community needs/resources UI
│   │   ├── lib/
│   │   │   └── supabase.ts      # Supabase frontend client
│   │   └── App.tsx              # root layout + state
│   └── .env.example
├── .github/
│   └── workflows/               # CI/CD pipelines
├── README.md
└── LICENSE
```

---

## Known Limitations

- No user authentication — needs and resources are anonymous
- NOAA weather alerts cover US only (USGS and EONET are global)
- Haversine matching ignores road networks and terrain
- No push notifications for new nearby events
- No offline/PWA support

---

## Potential Improvements

- ML anomaly detection to predict emerging disaster clusters
- Social media feed integration for crowdsourced early warning
- Road-network routing to replace straight-line distance matching
- Push notifications via browser or SMS
- User authentication and trust scoring for posted needs
- Progressive Web App with offline caching

---

## License

MIT — free to use, modify, and distribute.

---

*Built with free infrastructure. No API keys purchased. No cloud bills.*