from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    OSM_FILE = os.getenv("OSM_FILE")

    CITY_OBJECTS = {
        "subway": {"key": "railway", "value": "subway_entrance"},
        "pharmacy": {"key": "amenity", "value": "pharmacy"},
        "kindergarten": {"key": "amenity", "value": "kindergarten"},
        "school": {"key": "amenity", "value": "school"},
        "bank": {"key": "amenity", "value": "bank"},
        "supermarket": {"key": "shop", "value": "supermarket"},
        "convenience": {"key": "shop", "value": "convenience"},
        "mall": {"key": "shop", "value": "mall"},
    }


settings = Settings()
