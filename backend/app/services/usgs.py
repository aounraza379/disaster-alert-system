import httpx
from app.core.database import supabase

from datetime import datetime, timezone

USGS_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "summary/2.5_day.geojson"
)

async def fetch_earthquakes():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(USGS_URL)
        response.raise_for_status()
        data = response.json()

    earthquakes = []
    for feature in data["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        earthquakes.append({
            "id": feature["id"],
            "magnitude": props["mag"],
            "place": props["place"],
            "time": props["time"],
            "longitude": coords[0],
            "latitude": coords[1],
            "depth_km": coords[2],
            "url": props["url"],
        })

    return earthquakes

async def save_earthquakes(earthquakes: list):
    try:
        rows = []
        for quake in earthquakes:
            rows.append({
                "id": quake["id"],
                "type": "earthquake",
                "title": quake["place"],
                "magnitude": quake["magnitude"],
                "place": quake["place"],
                "latitude": quake["latitude"],
                "longitude": quake["longitude"],
                "depth_km": quake["depth_km"],
                "event_time": datetime.fromtimestamp(
                    quake["time"] / 1000, tz=timezone.utc
                ).isoformat(),
                "source": "USGS",
                "url": quake["url"],
            })
        supabase.table("events").upsert(rows).execute()
        print(f"Saved {len(rows)} earthquakes to database")
    except Exception as e:
        print("ERROR saving earthquakes:", str(e))