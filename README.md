# Disaster Alert & Community Response System with Spatial-Trust Framework
# Created: April 2026 | Author: Aoun Raza 
---

## IMPORTANT NOTE FOR FUTURE AI OR HUMAN READING THIS

This document contains 100% of the project context built over multiple sessions.
The developer (Aoun) is an intermediate-level coder on Windows using VS Code.

---

## 1. PROJECT OVERVIEW

### What is this project?
A full-stack web application that:
1. Monitors real global disasters (earthquakes, wildfires, storms, volcanoes) in real time
2. Displays them on an interactive world map
3. Lets community members post what they need (water, food, medical help) and what they can offer
4. Automatically matches needs with nearby resources using a distance algorithm
5. Scores every community post with a trust rating to detect fake or malicious posts

### What problem does it solve?
When disasters happen, two problems exist simultaneously:
- People don't know WHERE disasters are happening in real time
- People who need help cannot find people who can help them nearby

Existing platforms (FEMA, Red Cross apps) are institutional — they work at government scale, not community scale. No lightweight, open, real-time tool existed that connected survivors to local volunteers using GPS-based matching.

### Who is it for?
- Survivors of disasters who need help
- Volunteers who want to offer help
- Relief organizations coordinating response
- Researchers studying disaster response systems
- Developers learning full-stack real-time applications

### Why is it important?
- Uses zero-cost infrastructure (no API keys purchased, no cloud bills)
- Pulls from official government sources (USGS, NASA)
- Adds an original trust/security layer no similar open project has
- Applicable to Pakistan and globally
- Academically publishable as a research contribution

---

## 2. CORE IDEA & SYSTEM LOGIC

### Simple explanation
Think of it like Google Maps + a community bulletin board + a spam filter, all built for disasters.

### Real-world analogy
Imagine a city floods. Right now:
- TV shows you the flood happened (like our disaster map)
- Someone needs insulin near their house (like our "Post a Need" feature)
- A pharmacist 4km away has extra insulin (like our "Post a Resource" feature)
- Our system connects them automatically (like our matching algorithm)
- But what if someone fake-posts a need to misdirect rescue teams? Our trust score catches that (Spatial-Trust framework)

### Step-by-step flow
```
Step 1: Every 60 seconds, backend asks USGS: "Any new earthquakes?"
Step 2: Every 120 seconds, backend asks NASA EONET: "Any wildfires/storms?"
Step 3: New events are saved to Supabase database
Step 4: Supabase instantly pushes new events to all open browsers via WebSocket
Step 5: Map markers appear on user screens without page refresh
Step 6: User clicks "Community" tab, sees posted needs and resources
Step 7: User posts a need with their GPS coordinates
Step 8: System calculates trust score (0.0 to 1.0) for that post
Step 9: User clicks "Match" — system finds resources within 50km in same category
Step 10: User sees matched resources sorted by distance
```

---

## 3. FULL SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                     USER'S BROWSER                          │
│  React + TypeScript + Vite                                  │
│  MapLibre GL JS (interactive map)                           │
│  OpenFreeMap tiles (no API key needed)                      │
│  Supabase JS client (receives real-time WebSocket updates)  │
│  URL: disaster-alert-system-beta.vercel.app                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
              HTTP requests + WebSocket
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   FASTAPI BACKEND                           │
│  Python 3.10 + Uvicorn (ASGI server)                       │
│  APScheduler (runs background jobs every 60s)               │
│  Haversine algorithm (calculates distances)                 │
│  Spatial-Trust engine (calculates trust scores)             │
│  URL: disaster-alert-system-production-b20a.up.railway.app  │
└──────┬──────────────────────────────────────┬───────────────┘
       │                                      │
  httpx async requests                  supabase-py client
       │                                      │
┌──────▼──────────┐              ┌────────────▼───────────────┐
│  EXTERNAL APIs  │              │  SUPABASE (DATABASE)        │
│                 │              │  PostgreSQL database         │
│  USGS API       │              │  Tables: events, needs,     │
│  (earthquakes)  │              │  resources, vouches,        │
│  No API key     │              │  disaster_zones             │
│                 │              │  Realtime: WebSocket push   │
│  NASA EONET     │              │  on every INSERT            │
│  (wildfires,    │              │  RLS: Row Level Security    │
│  storms, etc)   │              │  enabled on all tables      │
│  No API key     │              │                             │
└─────────────────┘              └─────────────────────────────┘
```

### How data flows
1. APScheduler (inside FastAPI) calls USGS every 60 seconds
2. USGS returns GeoJSON with earthquake data
3. FastAPI flattens the nested GeoJSON into clean objects
4. FastAPI calls `supabase.table("events").upsert(rows)` to save
5. Supabase detects the INSERT, broadcasts via WebSocket to all connected clients
6. React receives the WebSocket message, updates `events` state
7. MapLibre re-renders markers on the map automatically
8. User sees new earthquake marker appear without refreshing the page

---

## 4. TECH STACK & TOOLS

| Tool | Purpose | Why chosen |
|------|---------|-----------|
| Python 3.10 | Backend language | Strong async support, FastAPI requires it |
| FastAPI | Web framework | Auto-generates API docs, async-first, fast |
| Uvicorn | ASGI server | Required to run FastAPI in production |
| httpx | HTTP client | Async HTTP requests to USGS/NASA APIs |
| APScheduler | Background jobs | Polls APIs automatically every 60s |
| python-dotenv | Env variables | Reads .env file, keeps secrets out of code |
| Pydantic v2 | Data validation | Ensures bad data never enters the system |
| supabase-py | Database client | Official Python SDK for Supabase |
| React 18 | Frontend framework | Component-based, fast, widely used |
| TypeScript | Typed JavaScript | Catches errors at compile time |
| Vite | Build tool | Fastest React dev server available |
| Tailwind CSS | Styling | Utility-first, no separate CSS files needed |
| MapLibre GL JS | Interactive map | Open-source WebGL maps, zero cost |
| OpenFreeMap | Map tiles | No API key, no cost, OpenStreetMap data |
| @supabase/supabase-js | Frontend DB client | Real-time subscriptions from browser |
| Supabase | Backend-as-a-service | Free PostgreSQL + WebSocket + Auth |
| Railway | Backend hosting | Free tier, auto-deploys from GitHub |
| Vercel | Frontend hosting | Free, global CDN, auto-deploys from GitHub |
| USGS Earthquake API | Earthquake data | Official US government, free, no key |
| NASA EONET API | Natural events data | Official NASA, free, no key |

---

## 5. FEATURES IMPLEMENTED

### Feature 1: Live Disaster Map
- Pulls earthquake data from USGS every 60 seconds
- Pulls wildfire/storm/volcano data from NASA EONET every 120 seconds
- Displays colored circular markers on WebGL map
- Red = M5+, Orange = M3.5+, Yellow = M2.5+, Blue = natural events
- Marker size scales with earthquake magnitude
- Click any marker to see a dark popup with event details
- Map uses OpenFreeMap dark style tiles (no API key, no cost)

### Feature 2: Real-time Updates (WebSocket)
- Supabase Realtime is enabled on the `events` table
- When scheduler saves new events to database, Supabase instantly pushes them to all browsers
- React receives the push via `supabase.channel()` subscription
- New markers appear on map without any page refresh
- This is true real-time, not polling

### Feature 3: Disaster Event Sidebar
- Right sidebar lists all events from database
- Sorted by event_time descending (newest first)
- Shows magnitude badge with color coding
- Shows category badge for natural events
- Clicking an event flies the map to that location and opens popup
- Filter buttons at top: All / Earthquakes / Natural Events

### Feature 4: Community Needs Board
- Users post needs with: name, description, category, GPS coordinates
- Categories: water, food, medical, shelter, rescue, other
- Posts appear in the "Needs" tab in the Community panel
- Each need shows a trust score bar (green/orange/red)
- Shows location verified icon (📍 or ⚠️)

### Feature 5: Community Resources Board
- Users post resources with same fields as needs
- Resources appear in "Resources" tab
- Resources have is_available flag (true by default)

### Feature 6: Proximity Matching Algorithm
- User clicks "Match" on any need
- System calls `GET /api/match/{need_id}`
- Backend fetches all available resources in same category
- Runs Haversine formula to calculate distance between need and each resource
- Filters resources within 50km radius
- Returns sorted list (closest first) with distance_km value
- Frontend displays matches under the need

### Feature 7: Spatial-Trust Framework (ORIGINAL FEATURE)
This is the unique research contribution. Every need and resource post gets a trust score from 0.0 to 1.0.

Three filters calculate the score:

**Filter 1 — Proof of Location (max 0.4 points)**
- Checks if post GPS coordinates are within 150km of any known disaster event in database
- If yes: location_score = 0.4 (hard to fake — you'd need real GPS near real disaster)
- If no: location_score = 0.1 (suspicious — why post from 500km away?)

**Filter 2 — Social Vouching (max 0.4 points)**
- Other users within 50km can vouch for a post via `POST /api/vouch`
- Each vouch adds 0.1 to vouch_score, capped at 0.4
- Voucher must be physically near the post (within 50km) to vouch

**Filter 3 — Temporal Decay (max 0.2 points)**
- Fresh post (under 6 hours): temporal = 0.2
- 6-12 hours old: temporal = 0.15
- 12-24 hours old: temporal = 0.10
- Over 24 hours old: temporal = 0.05
- APScheduler runs decay every 6 hours automatically

**Total trust score = location + vouching + temporal (max 1.0)**

Real survivor near disaster + 3 vouches + fresh = 0.4 + 0.3 + 0.2 = 0.9 (high trust)
Fake post from 500km + no vouches + 24h old = 0.1 + 0.0 + 0.05 = 0.15 (flagged)

### Feature 8: Simulation & Experiment
- `backend/simulation.py` generates 1000 posts (700 real, 300 fake/Sybil)
- Real posts: inside disaster zone, recent, some vouches
- Fake posts: 300-800km away, old, no vouches
- At threshold 0.3: 100% Precision, 100% Recall, 100% Accuracy
- Results saved to `simulation_results.json`

---

## 6. CODEBASE STRUCTURE

```
disaster-alert-system/
│
├── backend/                          ← Python FastAPI application
│   ├── app/
│   │   ├── __init__.py               ← Makes app a Python package
│   │   ├── main.py                   ← ENTRY POINT. Creates FastAPI app, registers routes, starts scheduler
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── matching.py           ← Routes for needs, resources, vouching, matching
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             ← Reads SUPABASE_URL and SUPABASE_KEY from .env
│   │   │   ├── database.py           ← Creates single shared Supabase client
│   │   │   └── scheduler.py          ← APScheduler setup, poll_earthquakes, poll_events, decay_trust_scores jobs
│   │   │
│   │   ├── models/                   ← Empty folder, reserved for future database models
│   │   │
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── usgs.py               ← fetch_earthquakes() and save_earthquakes() functions
│   │       ├── eonet.py              ← fetch_natural_events() and save_events() functions
│   │       └── trust.py              ← verify_location(), calculate_vouch_weight(), calculate_temporal_decay(), calculate_trust_score()
│   │
│   ├── tests/                        ← Empty, reserved for pytest tests
│   ├── venv/                         ← Python virtual environment (NOT committed to git)
│   ├── simulation.py                 ← Standalone script to test Spatial-Trust accuracy
│   ├── simulation_results.json       ← Output of simulation (700 real, 300 fake posts tested)
│   ├── requirements.txt              ← All Python dependencies with versions
│   ├── Procfile                      ← Railway start command: web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
│   ├── runtime.txt                   ← python-3.10.10 (tells Railway which Python version)
│   ├── render.yaml                   ← Render deployment config (kept but using Railway instead)
│   ├── .env                          ← NEVER COMMITTED. Contains SUPABASE_URL and SUPABASE_KEY
│   └── .env.example                  ← Template showing variable names without values
│
├── frontend/                         ← React + TypeScript application
│   ├── src/
│   │   ├── main.tsx                  ← React entry point. Imports MapLibre CSS here.
│   │   ├── App.tsx                   ← Root component. State management, layout, filters, sidebar tabs
│   │   │
│   │   ├── components/
│   │   │   ├── DisasterMap.tsx       ← MapLibre map with markers, popups, flyTo on selection
│   │   │   └── NeedsPanel.tsx        ← Community panel: needs list, resources list, post form, trust bars
│   │   │
│   │   ├── lib/
│   │   │   └── supabase.ts           ← Creates Supabase browser client using VITE_ env vars
│   │   │
│   │   └── index.css                 ← Only contains: @import "tailwindcss"; + MapLibre popup overrides
│   │
│   ├── public/                       ← Static assets
│   ├── .env.local                    ← NEVER COMMITTED. Contains VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL
│   ├── .env.example                  ← Template
│   ├── vite.config.ts                ← Vite config with React and Tailwind plugins
│   ├── tailwind.config.js            ← Tailwind configuration
│   ├── tsconfig.json                 ← TypeScript configuration
│   └── package.json                  ← NPM dependencies
│
├── .github/
│   └── workflows/                    ← GitHub Actions CI/CD (empty, reserved)
│
├── README.md                         ← Professional project documentation
├── .gitignore                        ← Ignores: venv/, node_modules/, .env, .env.local, __pycache__
└── LICENSE                           ← MIT License
```

### Key functions explained simply

**`backend/app/main.py`**
- `lifespan()` — runs when server starts and stops. Starts the scheduler on startup.
- `get_earthquakes()` — when someone calls GET /api/earthquakes, fetch from USGS and save to DB
- `get_events()` — when someone calls GET /api/events, fetch from NASA and save to DB

**`backend/app/core/scheduler.py`**
- `poll_earthquakes()` — called automatically every 60 seconds, fetches and saves earthquakes
- `poll_events()` — called automatically every 120 seconds, fetches and saves natural events
- `decay_trust_scores()` — called every 6 hours, reduces trust scores of old posts

**`backend/app/services/usgs.py`**
- `fetch_earthquakes()` — calls USGS API, flattens GeoJSON into clean list of dicts
- `save_earthquakes(earthquakes)` — bulk upserts all earthquakes in ONE database call (not a loop)

**`backend/app/services/trust.py`**
- `haversine(lat1,lon1,lat2,lon2)` — returns km distance between two GPS points
- `verify_location(lat,lon)` — checks if coordinates are within 150km of any disaster event
- `calculate_trust_score(...)` — runs all 3 filters, returns score + breakdown dict

**`backend/app/api/matching.py`**
- `post_need()` — saves need, immediately calculates and saves trust score
- `post_resource()` — saves resource, immediately calculates and saves trust score
- `vouch_for_post()` — checks voucher is within 50km, saves vouch, recalculates trust
- `match_need_to_resources()` — finds resources within radius, sorted by distance

**`frontend/src/components/DisasterMap.tsx`**
- First `useEffect` — initializes MapLibre map with OpenFreeMap dark style
- Second `useEffect` — runs when events change, adds/removes markers
- Third `useEffect` — runs when selectedId changes, flies map to selected event

**`frontend/src/App.tsx`**
- First `useEffect` — loads events from Supabase, sets up Realtime subscription
- `filtered` — computed list based on active filter (all/earthquake/natural_event)

---

## 7. CURRENT STATE

### Fully completed
- FastAPI backend with all routes working
- USGS earthquake data pipeline (fetch → save → display)
- NASA EONET natural events pipeline (fetch → save → display)
- APScheduler background polling (60s earthquakes, 120s events)
- Supabase database with all 5 tables (events, needs, resources, vouches, disaster_zones)
- Row Level Security policies on all tables
- Supabase Realtime enabled on events, needs, resources tables
- React frontend with live map
- MapLibre GL JS with OpenFreeMap tiles (dark style)
- Disaster markers with color coding and size scaling
- Sidebar with event list and filters
- Community panel with needs and resources tabs
- Post form for needs and resources
- Proximity matching algorithm (Haversine)
- Spatial-Trust framework (all 3 filters)
- Trust score visualization (colored bars in UI)
- Vouching system with proximity check
- Temporal decay scheduler job
- Simulation script with results (100% precision/recall at threshold 0.3)
- Railway backend deployment (ACTIVE, Online)
- Vercel frontend deployment (ACTIVE, Ready)
- Professional README.md

### Partially completed
- **CORS configuration** — trailing slash issue in main.py causing "Failed to fetch" from Vercel
- **VITE_API_URL in Vercel** — may be pointing to wrong Railway URL (need to verify)
- **Railway free credit** — 3 days / $4.36 left, needs monitoring or alternative hosting
- **GitHub Actions CI/CD** — folder exists but no workflow files written yet

### Not started
- Push notifications for nearby disasters
- Pakistan-specific data (PDMA/PMD APIs)
- Rate limiting on POST endpoints
- User authentication (Supabase Auth)
- Historical disaster search
- Mobile PWA / offline support
- SMS alerts

---

## 8. PENDING TASKS & ROADMAP

### IMMEDIATE (fix before anything else)
1. Fix CORS in `backend/app/main.py` — remove trailing slashes from allow_origins
2. Verify `VITE_API_URL` in Vercel environment variables points to correct Railway URL
3. Redeploy Vercel after fixing env var
4. Confirm Match and Post buttons work from deployed URL

### SHORT-TERM (next session)
1. Add browser push notifications for M5+ earthquakes near a location
2. Add PDMA Pakistan API or PMD weather alerts as third data source
3. Add rate limiting: `pip install slowapi`, limit POST /api/needs to 5 requests per minute per IP
4. Write GitHub Actions workflow for auto-testing on push

### MEDIUM-TERM
1. Supabase Auth — email/GitHub login so user_id is populated
2. Historical earthquake search by region and date range
3. PWA manifest and service worker for offline caching

### LONG-TERM (research vision)
1. ML-based anomaly detection for predicting emerging disasters
2. Social media feed integration (Twitter/Bluesky API)
3. Road-network routing to replace straight-line distance
4. Trust score visualization on the map (needs shown as green/orange/red dots)

---

## 9. LIMITATIONS & KNOWN ISSUES

### Current bugs
1. **"Failed to fetch" from Vercel** — CORS trailing slash issue + possibly wrong VITE_API_URL
2. **Railway credit expiring** — free trial has $4.36 left, will stop after 3 days without card

### Technical limitations
1. USGS data has 5-20 minute real-world delay (not instant earthquake alerts)
2. NASA EONET depends on satellite processing, can be hours delayed for wildfires
3. No Pakistan-specific local data sources
4. Haversine matching ignores roads, terrain, actual travel time
5. No user authentication — anyone can post anything
6. No rate limiting — vulnerable to spam flooding
7. Supabase free tier pauses after 7 days of inactivity
8. Railway free tier has credit limit

### Performance concerns
1. Trust score verification checks ALL events in database for every post — will slow down as database grows (fix: add PostGIS spatial index)
2. Bulk upsert saves all events in one call — good, but still runs every 60 seconds
3. Temporal decay runs on ALL unresolved needs every 6 hours — will be slow at scale

---

## 10. KEY DECISIONS & REASONING

| Decision | Reason |
|----------|--------|
| FastAPI over Flask | Async-first, auto API docs, better for WebSocket support |
| Supabase over Firebase | SQL database, open source, free Realtime, no vendor lock-in |
| MapLibre over Google Maps | Zero cost, no API key, open source license |
| OpenFreeMap over Mapbox | No registration, no API key, production-quality tiles |
| Railway over Render | Render free tier sleeps after 15 minutes of inactivity; Railway stays alive |
| Haversine over PostGIS ST_Distance | Simpler to implement, sufficient accuracy for disaster scale distances |
| Bulk upsert over loop | One database round trip instead of 80 — prevents timeout |
| Supabase Realtime over FastAPI WebSocket | Supabase handles the WebSocket infrastructure for free |
| venv inside backend/ | Keeps dependencies isolated from system Python |
| Python 3.10 for venv | Compatible with all packages (supabase-py, APScheduler); Python 3.14 was system default but incompatible |

---

## 11. SETUP & REBUILD INSTRUCTIONS

### Prerequisites
- Windows PC
- Python 3.10+ installed (system has Python 3.14, but venv uses 3.10)
- Node.js 20+ installed
- Git installed
- VS Code installed
- GitHub account
- Supabase account (free, no card)
- Vercel account (free, connect with GitHub)
- Railway account (free trial)

### Step 1: Clone the repository
```
git clone https://github.com/aounraza379/disaster-alert-system.git
cd disaster-alert-system
```

### Step 2: Backend setup
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env` file:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

Get these from: supabase.com → your project → Settings → API

### Step 3: Run Supabase schema
Go to Supabase → SQL Editor → run this:
```sql
create extension if not exists postgis;
create extension if not exists "pgcrypto";

create table events (
    id text primary key,
    type text not null,
    title text,
    magnitude float,
    place text,
    category text,
    latitude float not null,
    longitude float not null,
    depth_km float,
    event_time timestamptz,
    source text,
    url text,
    created_at timestamptz default now()
);

create table needs (
    id uuid primary key default gen_random_uuid(),
    name text not null default 'Anonymous',
    user_id uuid,
    description text not null,
    category text not null,
    latitude float not null,
    longitude float not null,
    is_resolved boolean default false,
    trust_score float default 0.5,
    location_verified boolean default false,
    vouch_count integer default 0,
    reported_at timestamptz default now(),
    created_at timestamptz default now()
);

create table resources (
    id uuid primary key default gen_random_uuid(),
    name text not null default 'Anonymous',
    user_id uuid,
    description text not null,
    category text not null,
    latitude float not null,
    longitude float not null,
    is_available boolean default true,
    trust_score float default 0.5,
    location_verified boolean default false,
    vouch_count integer default 0,
    reported_at timestamptz default now(),
    created_at timestamptz default now()
);

create table vouches (
    id uuid primary key default gen_random_uuid(),
    post_id uuid not null,
    post_type text not null check (post_type in ('need', 'resource')),
    voucher_name text not null,
    voucher_latitude float not null,
    voucher_longitude float not null,
    created_at timestamptz default now()
);

create table disaster_zones (
    id uuid primary key default gen_random_uuid(),
    event_id text,
    name text not null,
    center_latitude float not null,
    center_longitude float not null,
    radius_km float not null default 100,
    source text,
    created_at timestamptz default now()
);

alter table events enable row level security;
alter table needs enable row level security;
alter table resources enable row level security;
alter table vouches enable row level security;
alter table disaster_zones enable row level security;

create policy "allow read events" on events for select using (true);
create policy "allow insert events" on events for insert with check (true);
create policy "allow upsert events" on events for update using (true);
create policy "allow all needs" on needs for all using (true) with check (true);
create policy "allow all resources" on resources for all using (true) with check (true);
create policy "allow all vouches" on vouches for all using (true) with check (true);
create policy "allow read zones" on disaster_zones for select using (true);
create policy "allow insert zones" on disaster_zones for insert with check (true);
```

Enable Realtime on events, needs, resources tables from Table Editor.

### Step 4: Run backend locally
```
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

OR

python -m uvicorn app.main:app --reload
```
Visit: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

### Step 5: Frontend setup
```
cd frontend
npm install
```

Create `frontend/.env.local`:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://127.0.0.1:8000
```

Run frontend:
```
npm run dev
```
Visit: http://localhost:5173

---

## 12. FUTURE IMPROVEMENTS

### Push Notifications (HIGH PRIORITY)
Install: `pip install pywebpush`
When M5+ earthquake saved, call Web Push API with user's subscription
Frontend registers service worker and requests notification permission

### Pakistan Data Sources
PDMA (Pakistan Disaster Management Authority): https://ndma.gov.pk/
PMD (Pakistan Meteorological Department): http://www.pmd.gov.pk/
Both have public situation reports. Integrate as a third scheduler job.

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
@app.post("/api/needs")
@limiter.limit("5/minute")
async def post_need(...):
```

### PostGIS Spatial Indexing
```sql
CREATE INDEX events_location_idx ON events USING GIST (
    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
);
```
This makes location queries 100x faster as database grows.

---

## 13. BEGINNER EXPLANATION

Imagine you have a friend who watches the news 24/7 and whenever a disaster happens anywhere in the world, they tell you immediately on your phone without you asking.

That is what our system does — but instead of a friend, it is a computer program (the backend) checking official government websites (USGS for earthquakes, NASA for fires) every minute and putting the information on a map you can see in your browser.

Now imagine during the disaster, people in the affected area can send a text message to a shared board saying "I need clean water at my location" and volunteers can post "I have water supplies near me." Another program in the system (the matching algorithm) reads both messages and says "these two people are only 6km apart — connect them."

But what if someone is not actually in the disaster area and sends a fake message to confuse the rescue teams? That is where the trust score comes in. The system checks: Is this person's GPS location near a real disaster? Have other people nearby confirmed their message? Is the message recent or very old? Based on these three checks, every message gets a score. High score = trustworthy, low score = suspicious.

All of this was built for free, using no paid services, and is now accessible on the internet for anyone to use.

---

## 14. FUTURE AI HANDOFF NOTES

### Things that must NOT be changed without understanding

1. **The venv uses Python 3.10, NOT Python 3.14**
   System Python is 3.14 but venv is 3.10. If someone upgrades the venv to 3.14, supabase-py and other packages may break. Always activate venv before running Python commands.

2. **Bulk upsert pattern in usgs.py**
   The save function builds a list first, then calls upsert ONCE. If anyone changes this to a loop (one upsert per earthquake), it will timeout with 80+ earthquakes.

3. **CORS allow_origins must NOT have trailing slashes**
   "https://example.com/" with a slash will cause "Failed to fetch" from the frontend. Always use URLs without trailing slashes.

4. **Supabase Realtime must be enabled on the events table**
   This is set in the Supabase dashboard, not in code. If the project is moved to a new Supabase project, Realtime must be re-enabled manually on events, needs, and resources tables.

5. **lifespan() must be defined BEFORE app = FastAPI()**
   Python reads files top-to-bottom. If lifespan is defined after the FastAPI instance, it will not be found and the app will crash.

6. **Railway URL contains "production-b20a" in the subdomain**
   Full URL: `disaster-alert-system-production-b20a.up.railway.app`
   This is different from `disaster-alert-system.up.railway.app`. Always use the full URL.

7. **Trust score calculation is intentionally simple**
   The three-filter system was designed to be academically defensible and easy to explain. Do not add complexity without updating the research paper accordingly.

8. **simulation.py is standalone — it does not import from the app**
   It has its own haversine and trust calculation functions copied inline. This was intentional to allow running it without the full app environment.

### Hidden assumptions
- USGS feed returns magnitude 2.5+ events from the last day (summary/2.5_day.geojson)
- NASA EONET returns a maximum of 50 open events per request (limit=50 parameter)
- Haversine accuracy is sufficient for disaster-scale distances (error < 0.5% for distances under 1000km)
- Trust threshold of 0.3 was determined from simulation — below 0.3 = suspicious

### Design logic
- The project was built in phases, each phase tested before moving to next
- Every new feature was committed to GitHub before starting the next
- The matching algorithm uses category matching FIRST, then distance — this prevents cross-category false matches
- The vouching system requires proximity (50km) because remote vouching would defeat the purpose

---

*Last updated: April 8, 2026*
*GitHub: https://github.com/aounraza379/disaster-alert-system*
*Frontend: https://disaster-alert-system-beta.vercel.app*
*Backend: https://disaster-alert-system-production-b20a.up.railway.app* 
