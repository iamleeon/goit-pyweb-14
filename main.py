from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from src.routes import contacts, auth, users
from src.conf.config import settings

import redis.asyncio as redis


app = FastAPI(
    title="Contact Management API",
    description="API for managing contacts with CRUD operations.",
    version="1.0.0",
)

origins = [
    "http://localhost:3000"
    ]

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """
    Initialize Redis and FastAPILimiter during the startup event.

    :rtype: None
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/health", tags=["Health check"])
def health_check():
    """
    Health check endpoint to verify if the API is up and running.

    :return: A JSON response indicating the API status.
    :rtype: dict
    """
    return {"status": "healthy"}

