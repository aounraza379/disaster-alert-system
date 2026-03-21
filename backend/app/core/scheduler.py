from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

def start_scheduler(app):
    from app.services.usgs import fetch_earthquakes, save_earthquakes
    from app.services.eonet import fetch_natural_events, save_events

    async def poll_earthquakes():
        print("Polling USGS...")
        data = await fetch_earthquakes()
        await save_earthquakes(data)
        print(f"Polled {len(data)} earthquakes")

    async def poll_events():
        print("Polling NASA EONET...")
        data = await fetch_natural_events()
        await save_events(data)
        print(f"Polled {len(data)} events")

    scheduler.add_job(poll_earthquakes, IntervalTrigger(seconds=60))
    scheduler.add_job(poll_events, IntervalTrigger(seconds=120))
    scheduler.start()