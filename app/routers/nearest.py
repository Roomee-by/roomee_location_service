from fastapi import APIRouter
from app.services.geocode_service import find_nearby
from app.logs.logger import logger


router = APIRouter(prefix="/nearest", tags=["Nearby"])


@router.get("/")
async def nearest(lat: float, lon: float, radius: int = 500):
    logger.info(f"Get nearest objects for lat: {lat}, lon: {lon}, radius: {radius}")
    nearby = find_nearby(lat, lon, radius)
    logger.info(f"Nearby for {lat}, {lon}, {radius} → {nearby}")
    return nearby
