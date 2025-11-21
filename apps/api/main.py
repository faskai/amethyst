"""Amethyst API Server."""

import logging

from app_routes import router as app_router
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resource_routes import router as resource_router

# Load .env from monorepo root (searches parent directories)
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Amethyst API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8083",
        "https://biz.fask.ai",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_router)
app.include_router(resource_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}
