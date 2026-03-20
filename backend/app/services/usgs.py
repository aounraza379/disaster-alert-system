import httpx

USGS_URL = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "summary/2.5_day.geojson"
)

async def fetch_earthquakes():
    async with httpx.AsyncClient() as client:
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