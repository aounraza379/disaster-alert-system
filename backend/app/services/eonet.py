import httpx

EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&limit=50"

async def fetch_natural_events():
    async with httpx.AsyncClient() as client:
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