from fastapi import APIRouter
from app.services.geocode_service import get_district_by_point, find_nearby
from app.logs.logger import logger

router = APIRouter(prefix="/geocode", tags=["Geocode"])


@router.get("/")
async def enrich(lat: float, lon: float, city: str, radius: int = 500):
    logger.info(f"Get district and nearby objects for lat: {lat}, lon: {lon}, city: {city}, radius: {radius}")

    district = get_district_by_point(lat, lon, city)
    district = district.get("district", "")
    nearby = find_nearby(lat, lon, radius)

    logger.info(f"District: {district}, nearby objects: {nearby} for {lat}, {lon}, {city}, {radius}m")

    return {
        "district": district,
        "nearby": nearby
    }
