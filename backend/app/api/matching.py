from fastapi import APIRouter
from pydantic import BaseModel
from app.core.database import supabase
import math
from app.services.trust import calculate_trust_score

router = APIRouter(prefix="/api", tags=["matching"])

# --- Pydantic models ---
# These define and validate the shape of data coming INTO your API

class NeedIn(BaseModel):
    name: str
    description: str
    category: str
    latitude: float
    longitude: float

class ResourceIn(BaseModel):
    name: str
    description: str
    category: str
    latitude: float
    longitude: float

# --- Haversine distance formula ---
# Calculates real-world km distance between two lat/lng points
# This is the math that powers proximity matching

def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# --- Routes ---

@router.post("/needs")
async def post_need(need: NeedIn):
    result = supabase.table("needs").insert(need.model_dump()).execute()
    
    if result.data:
        posted = result.data[0]
        trust = calculate_trust_score(
            post_lat=posted["latitude"],
            post_lon=posted["longitude"],
            post_id=posted["id"],
            post_type="need",
            reported_at=posted["created_at"]
        )
        supabase.table("needs").update({
            "trust_score": trust["trust_score"],
            "location_verified": trust["location_verified"]
        }).eq("id", posted["id"]).execute()

        return {"message": "Need posted", "data": posted, "trust": trust}
    
    return {"message": "Need posted", "data": result.data}

@router.post("/resources")
async def post_resource(resource: ResourceIn):
    result = supabase.table("resources").insert(resource.model_dump()).execute()
    
    if result.data:
        posted = result.data[0]
        trust = calculate_trust_score(
            post_lat=posted["latitude"],
            post_lon=posted["longitude"],
            post_id=posted["id"],
            post_type="resource",
            reported_at=posted["created_at"]
        )
        supabase.table("resources").update({
            "trust_score": trust["trust_score"],
            "location_verified": trust["location_verified"]
        }).eq("id", posted["id"]).execute()

        return {"message": "Resource posted", "data": posted, "trust": trust}

    return {"message": "Resource posted", "data": result.data}

@router.get("/needs")
async def get_needs():
    result = supabase.table("needs").select("*").eq("is_resolved", False).execute()
    return {"count": len(result.data), "needs": result.data}

@router.get("/resources")
async def get_resources():
    result = supabase.table("resources").select("*").eq("is_available", True).execute()
    return {"count": len(result.data), "resources": result.data}

@router.get("/match/{need_id}")
async def match_need_to_resources(need_id: str, radius_km: float = 50):
    # get the need
    need_result = supabase.table("needs").select("*").eq("id", need_id).execute()
    if not need_result.data:
        return {"error": "Need not found"}

    need = need_result.data[0]

    # get all available resources in same category
    resources_result = supabase.table("resources") \
        .select("*") \
        .eq("is_available", True) \
        .eq("category", need["category"]) \
        .execute()

    # filter by proximity using haversine
    matches = []
    for resource in resources_result.data:
        distance = haversine(
            need["latitude"], need["longitude"],
            resource["latitude"], resource["longitude"]
        )
        if distance <= radius_km:
            matches.append({**resource, "distance_km": round(distance, 2)})

    # sort closest first
    matches.sort(key=lambda x: x["distance_km"])

    return {
        "need": need,
        "matches": matches,
        "radius_km": radius_km
    }

class VouchIn(BaseModel):
    post_id: str
    post_type: str
    voucher_name: str
    latitude: float
    longitude: float

@router.post("/vouch")
async def vouch_for_post(vouch: VouchIn):
    # verify voucher is near the post
    if vouch.post_type == "need":
        post_result = supabase.table("needs").select("*").eq("id", vouch.post_id).execute()
    else:
        post_result = supabase.table("resources").select("*").eq("id", vouch.post_id).execute()

    if not post_result.data:
        return {"error": "Post not found"}

    post = post_result.data[0]
    distance = haversine(vouch.latitude, vouch.longitude, post["latitude"], post["longitude"])

    if distance > 50:
        return {"error": f"You are {round(distance)}km away. Must be within 50km to vouch"}

    # save vouch
    supabase.table("vouches").insert({
        "post_id": vouch.post_id,
        "post_type": vouch.post_type,
        "voucher_name": vouch.voucher_name,
        "voucher_latitude": vouch.latitude,
        "voucher_longitude": vouch.longitude
    }).execute()

    # recalculate trust
    trust = calculate_trust_score(
        post_lat=post["latitude"],
        post_lon=post["longitude"],
        post_id=vouch.post_id,
        post_type=vouch.post_type,
        reported_at=post["created_at"]
    )

    table = "needs" if vouch.post_type == "need" else "resources"
    supabase.table(table).update({
        "trust_score": trust["trust_score"],
        "vouch_count": len(supabase.table("vouches").select("id").eq("post_id", vouch.post_id).execute().data)
    }).eq("id", vouch.post_id).execute()

    return {"message": "Vouch recorded", "new_trust_score": trust["trust_score"], "breakdown": trust["breakdown"]}