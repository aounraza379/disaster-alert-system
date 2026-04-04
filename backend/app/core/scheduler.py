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
    scheduler.add_job(decay_trust_scores, IntervalTrigger(hours=6))
    scheduler.start()

async def decay_trust_scores():
    from app.services.trust import calculate_temporal_decay
    
    # fetch all unresolved needs
    needs = supabase.table("needs").select("*").eq("is_resolved", False).execute()
    for need in needs.data:
        decay = calculate_temporal_decay(need["created_at"])
        new_score = round(need["trust_score"] * decay, 3)
        supabase.table("needs").update({"trust_score": new_score}).eq("id", need["id"]).execute()

    resources = supabase.table("resources").select("*").eq("is_available", True).execute()
    for resource in resources.data:
        decay = calculate_temporal_decay(resource["created_at"])
        new_score = round(resource["trust_score"] * decay, 3)
        supabase.table("resources").update({"trust_score": new_score}).eq("id", resource["id"]).execute()

    print("Trust scores decayed")