from fastapi import APIRouter
from pydantic import BaseModel
from app.core.database import supabase
import math

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
    return {"message": "Need posted", "data": result.data}

@router.post("/resources")
async def post_resource(resource: ResourceIn):
    result = supabase.table("resources").insert(resource.model_dump()).execute()
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