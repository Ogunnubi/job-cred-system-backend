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

# import secrets
#
# secret_key = secrets.token_urlsafe(32)
# print(secret_key)