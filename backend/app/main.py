from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db
from app.api.main import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
   init_db()
   yield
   print("App Finalizada")


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def welcome():
    return {"message": "Welcome to task app with FastAPI"}


app.include_router(api_router, prefix="/api/v1")
