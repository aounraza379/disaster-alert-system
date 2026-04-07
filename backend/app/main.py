from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.usgs import fetch_earthquakes, save_earthquakes
from app.services.eonet import fetch_natural_events, save_events
from app.core.scheduler import start_scheduler, scheduler
from app.api.matching import router as matching_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler(app)
    print("Scheduler started — polling every 60s")
    yield
    scheduler.shutdown()
    print("Scheduler stopped")

app = FastAPI(
    title="Disaster Alert System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://*.vercel.app",
        "https://disaster-alert-system.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matching_router)

@app.get("/")
async def root():
    return {"status": "online", "message": "Disaster Alert API running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/earthquakes")
async def get_earthquakes():
    data = await fetch_earthquakes()
    await save_earthquakes(data)
    return {"count": len(data), "events": data}

@app.get("/api/events")
async def get_events():
    data = await fetch_natural_events()
    await save_events(data)
    return {"count": len(data), "events": data}

