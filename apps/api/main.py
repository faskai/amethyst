"""Amethyst API Server."""

import asyncio
import json
import logging

from amethyst_engine import Engine
from amethyst_engine.app import App
from apps_dao import create_app, get_app, list_apps, update_app
from fastapi import FastAPI, HTTPException, Request
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


@app.get("/apps/")
async def list_apps_endpoint():
    """List all apps."""
    return list_apps()


@app.post("/apps/")
async def create_app_endpoint(request: Request):
    """Create new app."""
    body = await request.json()
    app_obj = App(**body)
    app_id = create_app(app_obj.model_dump())
    return {"id": app_id}


@app.get("/apps/{app_id}")
async def get_app_endpoint(app_id: str):
    """Get app by ID."""
    json_obj = get_app(app_id)
    if not json_obj:
        raise HTTPException(status_code=404, detail="App not found")
    return {"id": app_id, **json_obj}


@app.post("/apps/{app_id}/runs")
async def create_run_endpoint(app_id: str):
    """Create new run and execute with streaming."""
    from uuid import uuid4

    json_obj = get_app(app_id)
    if not json_obj:
        raise HTTPException(status_code=404, detail="App not found")

    run_id = str(uuid4())

    async def stream():
        messages = asyncio.Queue()
        app_obj = App(**json_obj)

        def save_app_callback():
            update_app(
                app_id,
                app_obj.model_dump(
                    exclude={"memory": {"tasks": {"__all__": {"async_task"}}}}
                ),
            )

        engine = Engine(
            send_update=messages.put_nowait, save_app=save_app_callback, verbose=True
        )

        task = asyncio.create_task(engine.run(app_obj, run_id))

        while not task.done() or not messages.empty():
            if not messages.empty():
                update = await messages.get()
                yield f"data: {json.dumps(update)}\n\n"
            await asyncio.sleep(0)

        await task

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/apps/{app_id}/runs/{run_id}")
async def get_run_endpoint(app_id: str, run_id: str):
    """Get run by ID - returns the main task."""
    json_obj = get_app(app_id)
    if not json_obj:
        raise HTTPException(status_code=404, detail="App not found")

    app_obj = App(**json_obj)
    main_task = next(
        (t for t in app_obj.memory.tasks.values() if t.parent_task_id == run_id), None
    )
    if not main_task:
        raise HTTPException(status_code=404, detail="Run not found")

    return main_task.to_dict(include_ai_calls=True)
