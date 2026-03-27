from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.main import api_router


app = FastAPI()


@app.get('/')
async def welcome():
    return {"message": "Welcome to task app with FastAPI"}


app.include_router(api_router, prefix="/api/v1")
