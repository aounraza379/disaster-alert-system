import httpx
from app.core.database import supabase

EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=50"

async def fetch_natural_events():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(EONET_URL)
        response.raise_for_status()
        data = response.json()

    events = []
    for event in data["events"]:
        geometry = event["geometry"]
        if not geometry:
            continue
        latest = geometry[-1]
        coords = latest["coordinates"]
        events.append({
            "id": event["id"],
            "title": event["title"],
            "category": event["categories"][0]["title"],
            "date": latest["date"],
            "longitude": coords[0],
            "latitude": coords[1],
        })

    return events

async def save_events(events: list):
    try:
        rows = []
        for event in events:
            rows.append({
                "id": event["id"],
                "type": "natural_event",
                "title": event["title"],
                "category": event["category"],
                "latitude": event["latitude"],
                "longitude": event["longitude"],
                "event_time": event["date"],
                "source": "NASA EONET",
            })
        supabase.table("events").upsert(rows).execute()
        print(f"Saved {len(rows)} natural events to database")
    except Exception as e:
        print("ERROR saving events:", str(e))