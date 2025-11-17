"""Amethyst API Server."""

import asyncio
import json
import logging

from amethyst_engine import Engine
from amethyst_engine.app import AmtFile, App, Resource
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

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


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/run")
async def run_app(request: Request):
    body = await request.json()

    async def stream():
        messages = asyncio.Queue()

        app_obj = App(
            files=[AmtFile(**f) for f in body["files"]],
            resources={r["key"]: Resource(**r) for r in body.get("resources", [])},
            workspaceId=body["workspaceId"],
        )

        engine = Engine(send_update=messages.put_nowait, verbose=True)
        task = asyncio.create_task(engine.run(app_obj))

        while not task.done() or not messages.empty():
            if not messages.empty():
                update = await messages.get()
                yield f"data: {json.dumps(update)}\n\n"
            await asyncio.sleep(0)

        await task

    return StreamingResponse(stream(), media_type="text/event-stream")
