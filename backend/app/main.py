from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.services.usgs import fetch_earthquakes

from app.services.eonet import fetch_natural_events

app = FastAPI(
    title="Disaster Alert System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "online", "message": "Disaster Alert API running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/earthquakes")
async def get_earthquakes():
    data = await fetch_earthquakes()
    return {"count": len(data), "events": data}


@app.get("/api/events")
async def get_events():
    data = await fetch_natural_events()
    return {"count": len(data), "events": data}


