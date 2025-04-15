from fastapi import FastAPI
from contextlib import asynccontextmanager

from starlette.middleware.cors import CORSMiddleware

from app.db.mongo import mongodb
from app.routes import auth
import os

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Starting up...")
    await mongodb.connect()
    yield
    print("👋 Shutting down...")
    await mongodb.close()

app = FastAPI(lifespan=lifespan)

origins = [
        "http://localhost:5173",
        "http://localhost:3000"
    ]

app.add_middleware(
        CORSMiddleware,
        allow_origins = origins,
        allow_credentials = True,
        allow_methods = ["*"],
        allow_headers = ["*"]
    )

app.include_router(auth.router)