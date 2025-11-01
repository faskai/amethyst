"""Amethyst API Server."""

from typing import List

from amethyst_engine import Engine
from amethyst_engine.types import Resource
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(
    title="Amethyst API",
    version="0.1.0",
    description="AI-native programming language API",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    code: str
    resources: List[dict] = []


class RunResponse(BaseModel):
    status: str
    code: str
    result: str


@app.post("/v1/run", response_model=RunResponse)
async def run_code(request: RunRequest):
    """Execute Amethyst code."""
    try:
        # Convert to Resource objects
        resources = [Resource(**r) for r in request.resources]

        # Execute with engine
        engine = Engine(verbose=False)
        result = await engine.run(request.code, resources=resources)

        return RunResponse(
            status=result.get("status", "completed"),
            code=result.get("code", ""),
            result=result.get("result", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    return {"service": "Amethyst API", "docs": "/docs", "health": "/health"}
