from fastapi import FastAPI
from app.routers.district import router as district_router
from app.routers.nearest import router as nearest_router
from app.routers.geocode import router as geocode_router
from app.consumers.geolocation_consumer import geolocation_consumer
from app.logs.logger import logger
import asyncio
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
instrumentator = Instrumentator().instrument(app)


@app.on_event("startup")
async def startup():
    logger.info(".....[LOCATION SERVICE IS RUN].....")
    instrumentator.expose(app)
    asyncio.create_task(geolocation_consumer())



@app.get("/")
async def root():
    return {"message": "Location service is running"}


app.include_router(geocode_router)
app.include_router(district_router)
app.include_router(nearest_router)


