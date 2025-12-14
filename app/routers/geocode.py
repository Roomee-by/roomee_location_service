from fastapi import APIRouter
from app.services.geocode_service import get_district_by_point, find_nearby
from app.logs.logger import logger

router = APIRouter(prefix="/geocode", tags=["Geocode"])


@router.get("/")
async def enrich(lat: float, lon: float, city: str, radius: int = 500):
    """
    Дополняет данные объявления геоинформацией.

    Endpoint используется другими сервисами (parser service, post service)
    для получения:
        1. Административного района города.
        2. Объектов инфраструктуры, расположенных в пределах заданного радиуса

    Args:
        lat (float): широта объекта
        lon (float): долгота объекта
        city(str): город, внутри которого ищется район
        radius (int): радиус поиска объектов (в метрах), по умолчанию 500.


    Returns:
        dict: {
            "district": "<Название района>",
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
        - Логика определения района и поиска объектов инфраструктуры находится
        в geocode_service

        - Этот endpoint - общее решение "всё в одном" для дополнения геоинформацией
    """
    logger.info(f"Get district and nearby objects for lat: {lat}, lon: {lon}, city: {city}, radius: {radius}")

    district = get_district_by_point(lat, lon, city)
    district = district.get("district", "")
    nearby = find_nearby(lat, lon, radius)

    logger.info(f"District: {district}, nearby objects: {nearby} for {lat}, {lon}, {city}, {radius}m")

    return {
        "district": district,
        "nearby": nearby
    }
