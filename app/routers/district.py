from fastapi import APIRouter
from app.services.geocode_service import get_district_by_point
from app.logs.logger import logger

router = APIRouter(prefix="/district", tags=["District"])


@router.get("/")
async def get_district(lat: float, lon: float, city: str):
    logger.info(f"Get district for lat: {lat}, lon: {lon}, city: {city}")

    district = get_district_by_point(lat, lon, city)

    logger.info(f"District for lat: {lat}, lon: {lon}, city: {city} → {district}")

    return district
