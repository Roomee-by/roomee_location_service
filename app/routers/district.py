from fastapi import APIRouter
from app.services.geocode_service import get_district_by_point
from app.logs.logger import logger

router = APIRouter(prefix="/district", tags=["District"])


@router.get("/")
async def get_district(lat: float, lon: float, city: str):
    """
    Возвращает район города по координатам.

    Args:
         lat (float): широта
         lon (float): долгота
         city (str): город, в пределах которого выполняется поиск

    Returns:
        dict: словарь с найденным районом, например:
        {"district": "Советский"}

    Notes:
        - Этот endpoint используется parser service и другими частями
        системы, когда необходимо определить административный район для объявления.
        - Вся логика вычисления района лежит в geocode_service.get_district_by_point().
    """
    logger.info(f"Get district for lat: {lat}, lon: {lon}, city: {city}")

    district = get_district_by_point(lat, lon, city)

    logger.info(f"District for lat: {lat}, lon: {lon}, city: {city} → {district}")

    return district
