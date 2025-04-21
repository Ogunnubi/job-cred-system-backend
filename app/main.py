from fastapi import FastAPI
from contextlib import asynccontextmanager

from starlette.middleware.cors import CORSMiddleware

from fastapi.openapi.utils import get_openapi

from app.db.mongo import mongodb
from app.routes import auth, job, profile, credit

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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Your API",
        version="1.0.0",
        description="API for job platform",
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    if "schemas" not in openapi_schema["components"]:
        openapi_schema["components"]["schemas"] = {}

    exclude_paths = {
        "/signup": ["post"],
        "/login": ["post"],
        "/jobs/": ["post"]
    }

    for path, methods in openapi_schema["paths"].items():
        for method, config in methods.items():
            if path in exclude_paths and method.lower() in exclude_paths[path]:
                continue
            if config.get("security") is None:
                config["security"] = [{"Bearer": []}]

    for path_item in openapi_schema["paths"].values():
        for operation in path_item.values():
            if "requestBody" in operation:
                content = operation["requestBody"].get("content", {})
                for media_type in content.values():
                    if "$ref" in media_type.get("schema", {}):
                        ref = media_type["schema"]["$ref"]
                        if not ref.startswith("#/components/schemas/"):
                            media_type["schema"]["$ref"] = f"#/components/schemas/{ref}"

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
app.include_router(auth.router)
app.include_router(job.router, prefix="/jobs", tags=["jobs"])
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(credit.router, prefix="/credits", tags=["credits"])