import math
from datetime import datetime, timezone
from app.core.database import supabase

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# Filter 1 — Proof of Location
def verify_location(post_lat: float, post_lon: float, radius_km: float = 150) -> bool:
    result = supabase.table("events")\
        .select("latitude,longitude")\
        .gte("event_time", "2026-01-01")\
        .execute()
    
    for event in result.data:
        dist = haversine(post_lat, post_lon, event["latitude"], event["longitude"])
        if dist <= radius_km:
            return True
    return False

# Filter 2 — Social Weighting
def calculate_vouch_weight(post_id: str, post_type: str) -> float:
    vouches = supabase.table("vouches")\
        .select("*")\
        .eq("post_id", post_id)\
        .eq("post_type", post_type)\
        .execute()
    
    if not vouches.data:
        return 0.0
    
    weight = 0.0
    for vouch in vouches.data:
        # each vouch adds 0.1, capped at 0.4 total
        weight += 0.1
    return min(weight, 0.4)

# Filter 3 — Temporal Decay
def calculate_temporal_decay(reported_at_str: str) -> float:
    reported_at = datetime.fromisoformat(reported_at_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    hours_old = (now - reported_at).total_seconds() / 3600
    
    if hours_old <= 6:
        return 1.0       # full trust
    elif hours_old <= 12:
        return 0.75      # slight decay
    elif hours_old <= 24:
        return 0.5       # half trust
    else:
        return 0.25      # very old

# Master trust score calculator
def calculate_trust_score(
    post_lat: float,
    post_lon: float,
    post_id: str,
    post_type: str,
    reported_at: str
) -> dict:
    location_verified = verify_location(post_lat, post_lon)
    location_score = 0.4 if location_verified else 0.1
    vouch_score = calculate_vouch_weight(post_id, post_type)
    temporal_score = calculate_temporal_decay(reported_at) * 0.2

    total = round(location_score + vouch_score + temporal_score, 3)
    total = min(total, 1.0)

    return {
        "trust_score": total,
        "location_verified": location_verified,
        "breakdown": {
            "location": round(location_score, 3),
            "vouching": round(vouch_score, 3),
            "temporal": round(temporal_score, 3)
        }
    }