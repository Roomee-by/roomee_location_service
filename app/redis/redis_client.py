from redis import asyncio as aioredis
from dotenv import load_dotenv
import os

load_dotenv()

redis = aioredis.from_url(
    url=os.getenv("REDIS_SERVICE"),
    decode_responses=True
)
