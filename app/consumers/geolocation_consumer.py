import asyncio
import json
from app.redis.redis_client import redis
from app.services.geocode_service import get_district_by_point, find_nearby
from app.logs.logger import logger


RAW_STREAM = "raw_posts"
READY_STREAM = "geo_ready_posts"


async def geolocation_consumer():
    """
    Обрабатывает входящие raw_posts, добавляет к ним гео-информацию
    и отправляет в READY_STREAM.

    Поток данных:
        Parser service → (raw_posts) → Location  service
        Location service → (geo_ready_posts) → Posts service

    Операции:
        1. Чтение сообщений из Redis Stream.
        2. Декодирование входных данных и изображений.
        3. Определение района (disctrict) по координатам.
        4. Поиск объектов инфраструктуры вокруг дома. (квартиры, метро, аптеки и т.п)
        5. Формирование дополненного поста
        6. Отправка результата в geo_ready_posts
    """
    last_id = "0-0"
    logger.info("location service waiting for raw posts...")

    while True:
        try:
            response = await redis.xread(
                streams={RAW_STREAM: last_id},
                block=0,
                count=1
            )

            if not response:
                continue

            stream_name, messages = response[0]

            for message_id, fields in messages:
                last_id = message_id

                logger.info(f"location service recieved raw posts: {fields}")

                lat = float(fields.get("lat", 0))
                lon = float(fields.get("lon", 0))
                city = fields.get("city")

                images = json.loads(fields.get("images", "[]"))

                geo_district = get_district_by_point(lat, lon, city)
                geo_nearby_objects = find_nearby(lat, lon, radius=500)

                additional_fields = dict(fields)

                additional_fields["city_district"] = geo_district.get("district", "")

                additional_fields["nearby_subway"] = ", ".join(geo_nearby_objects.get("nearby", {}).get("subway", []))
                additional_fields["nearby_pharmacy"] = ", ".join(geo_nearby_objects.get("nearby", {}).get("pharmacy", []))
                additional_fields["nearby_kindergarten"] = ", ".join(geo_nearby_objects.get("nearby", {}).get("kindergarten", []))
                additional_fields["nearby_bank"] = ", ".join(geo_nearby_objects.get("nearby", {}).get("bank", []))
                additional_fields["nearby_school"] = ", ".join(geo_nearby_objects.get("nearby", {}).get("school", []))
                nearby_shop = []
                [nearby_shop.append(x) for x in [
                    *geo_nearby_objects.get("nearby", {}).get("supermarket", []),
                    *geo_nearby_objects.get("nearby", {}).get("convenience", []),
                    *geo_nearby_objects.get("nearby", {}).get("mall", [])
                ] if x not in nearby_shop]
                additional_fields["nearby_shop"] = ", ".join(nearby_shop)

                additional_fields["images"] = json.dumps(images)

                await redis.xadd(READY_STREAM, additional_fields)

                logger.info("location service add new fields to raw post & send to next queue")
        except Exception as e:
            logger.error(f"Error in location consumer: {e}")
            logger.info("Sleep 1 sec and try again")
            await asyncio.sleep(1)
