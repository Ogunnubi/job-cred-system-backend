from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.mongo import mongodb
from app.routes import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up...")
    await mongodb.connect()
    yield
    print("👋 Shutting down...")
    await mongodb.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)