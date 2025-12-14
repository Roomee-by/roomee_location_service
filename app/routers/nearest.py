from fastapi import APIRouter
from app.services.geocode_service import find_nearby
from app.logs.logger import logger


router = APIRouter(prefix="/nearest", tags=["Nearby"])


@router.get("/")
async def nearest(lat: float, lon: float, radius: int = 500):
    """
     Возвращает ближайшие объекты инфраструктуры вокруг заданной точки.

     Args:
         lat (float): широта
         lon (float): долгота
         radius (int): радиус поиска в метрах (по умолчанию 500)

    Returns:
        dict:
            {
            "nearby": {
                "subway": [...],
                "pharmacy": [...],
                "kindergarten": [...],
                "school": [...],
                "bank": [...],
                "supermarket": [...],
                ...
                }
            }

    Notes:
        - Использует функцию find_nearby(), которая выполняет геопоиск по OSM данным.
        - Этот endpoint предоставляет только данные об объектах, без определения района (для этого есть /geocode)
    """
    logger.info(f"Get nearest objects for lat: {lat}, lon: {lon}, radius: {radius}")
    nearby = find_nearby(lat, lon, radius)
    logger.info(f"Nearby for {lat}, {lon}, {radius} → {nearby}")
    return nearby
