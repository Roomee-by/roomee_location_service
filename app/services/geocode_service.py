from math import radians, sin, cos, asin, sqrt
import json
import osmium
from shapely.geometry import shape, Point
import random
from app.settings.settings import settings

POI_DATA = {key: [] for key in settings.CITY_OBJECTS.keys()}


class POIHandler(osmium.SimpleHandler):
    """
    Обработчик OSM-файла.

    Сканиурет:
    - nodes (узлы)
    - ways (линейные объекты: здания, дороги, контуры)

    И извлекает точки интереса (POI) по правилам, указанным в settings.CITY_OBJECTS
    """
    def node(self, n):
        """Обработка OSM-узлов (точек)"""
        if not n.tags:
            return

        for key, rule in settings.CITY_OBJECTS.items():
            if n.tags.get(rule["key"]) == rule["value"]:
                POI_DATA[key].append({
                    "name": n.tags.get("name:ru") or n.tags.get("name") or "",
                    "lat": n.location.lat,
                    "lon": n.location.lon
                })

    def way(self, w):
        """Обработка протяжённых объектов (way)."""
        for key, rule in settings.CITY_OBJECTS.items():
            if w.tags.get(rule["key"]) == rule["value"]:
                if w.nodes:
                    lat = sum(n.lat for n in w.nodes) / len(w.nodes)
                    lon = sum(n.lon for n in w.nodes) / len(w.nodes)

                    POI_DATA[key].append({
                        "name": w.tags.get("name:ru") or w.tags.get("name") or "",
                        "lat": lat,
                        "lon": lon
                    })


handler = POIHandler()
handler.apply_file(settings.OSM_FILE, locations=True)

"""for key, value in POI_DATA.items():
    print(f"  {key}:{len(value)} шт.")"""


def distance(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Вычисляет расстояние между двумя точками на сфере (формула хаверсинусов).
    Возвращает расстояние в метрах
    """
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2

    return 2 * R * asin(sqrt(a))


def find_nearby(lat: float, lon: float, radius: int = 500):
    """
    Ищет ближайшие объекты инфраструктуры в радиусе "radius",

    Алгоритм:
        1. Перебираем все POI определённого типа (из POI_DATA).
        2. Вычисляем расстояние до каждой точки.
        3. Если <= radius → добавляем в список.
        4. Оставляем максимум 5 уникальных объектов для каждого типа.

    Возвращает структуру вида:
    {"nearby": {"pharmacy": [...], "school": [...], ... }}
    """
    result = {k: set() for k in settings.CITY_OBJECTS.keys()}
    for key, poi_list in POI_DATA.items():
        for poi in poi_list:
            name = poi["name"].strip()
            if name and distance(lat, lon, poi["lat"], poi["lon"]) <= radius:
                result.setdefault(key, set()).add(name)
    cleaned = {k: random.sample(list(v), min(len(v), 5)) for k, v in result.items() if v and v != ''}
    return {"nearby": cleaned}


def load_district_geojson(city: str):
    """
    Загружает GeoJSON файл с полигонами районов города.
    Возвращает список: [(district_name, shapely_polygon), ...]
    """
    path = f"app/services/geo_files/{city}.geojson"
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    districts = []

    for feature in data['features']:
        props = feature['properties']

        name = props.get("name:ru")

        polygon = shape(feature['geometry'])
        districts.append((name, polygon))

    return districts


def get_unique_nearby_objects(nearby_objects: list, limit: int):
    """
    Возвращает список уникальных объектов, ограниченный limit.
    Используется как утилита.
    """
    if not nearby_objects or limit is None or limit < 1:
        return []
    return [obj for obj in set(nearby_objects) if obj != ''][:limit]


def get_district_by_point(lat: float, lon: float, city: str):
    """
    Определяет, к какому району города принадлежит точка (lat, lon).

    Алгоритм:
        1. Загружаем полигоны районов
        2. Создаём точку Point (lon, lat).
        3. Проверяем, какой полигон содержит точку.
        4. Если точка не попала ни в один район → возвращаем пустую строку.


    Возвращает:
        {"district": <name>}
    """
    districts = load_district_geojson(city)
    if lat != 0.0 and lon != 0.0:
        point = Point(lon, lat)

        for name, polygon in districts:
            if polygon.contains(point):
                return {"district": name}

    return {"district": ''}


if __name__ == "__main__":
    nearby = find_nearby(53.917755, 27.594841, 500)
    result = get_district_by_point(53.917755, 27.594841, "minsk")
    print(nearby)


