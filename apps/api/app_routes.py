"""App API routes."""

import asyncio
import json
from datetime import datetime, timezone

from amethyst_engine import Engine
from amethyst_engine.app import App, AppExpanded, ResourceExpanded
from apps_dao import create_app, get_app, list_apps, update_app
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from resources_dao import create_resource, get_resource

router = APIRouter(prefix="/apps", tags=["apps"])


def downcast_to_app(
    app_expanded: AppExpanded | App, resource_ids: list[str]
) -> tuple[App, datetime]:
    """Downcast AppExpanded to App, excluding resources and updating timestamp."""
    now = datetime.now(timezone.utc)
    app = App(
        **app_expanded.model_dump(exclude={"resources", "resource_ids", "updated_at"}),
        resource_ids=resource_ids,
        updated_at=now,
    )
    return app, now


def save_resources(resources: list[ResourceExpanded]) -> list[str]:
    """Save all resources and return all resource IDs."""
    resource_ids = []
    for resource in resources:
        if resource.id:
            create_resource(resource.id, resource.model_dump())
            resource_ids.append(resource.id)
    return resource_ids


def hydrate_app(app_id: str = None, app_expanded: AppExpanded = None) -> AppExpanded:
    """Load app and hydrate with resources from DB.

    Hydrates from:
    - app.resource_ids (saved resource IDs)
    - app.resources[i].id (resources that need full data from DB)
    """
    if app_id:
        json_obj = get_app(app_id)
        if not json_obj:
            raise HTTPException(status_code=404, detail="App not found")
        app_data = App(**json_obj)
        app_expanded = AppExpanded(
            files=app_data.files,
            resource_ids=app_data.resource_ids,
            workspaceId=app_data.workspaceId,
            memory=app_data.memory,
            resources=[],
        )

    # Hydrate from resource_ids and resources[i].id
    resource_ids_to_hydrate = set(app_expanded.resource_ids)
    for resource in app_expanded.resources:
        if resource.id:
            resource_ids_to_hydrate.add(resource.id)

    for resource_id in resource_ids_to_hydrate:
        resource_data = get_resource(resource_id)
        if resource_data:
            app_expanded.resources.append(ResourceExpanded(**resource_data))

    return app_expanded


@router.get("/")
async def list_apps_endpoint():
    """List all apps."""
    return list_apps()


@router.post("/")
async def create_app_endpoint(app_expanded: AppExpanded):
    """Create new app."""
    resource_ids = save_resources(app_expanded.resources)
    app_obj, now = downcast_to_app(app_expanded, resource_ids)
    app_id = create_app(app_obj.model_dump_json(), now)
    return {"id": app_id}


@router.get("/{app_id}")
async def get_app_endpoint(app_id: str):
    """Get app by ID with hydrated resources."""
    app_expanded = hydrate_app(app_id)
    return {"id": app_id, **app_expanded.model_dump()}


@router.post("/{app_id}/runs")
async def create_run_endpoint(app_id: str):
    """Plan and execute app with streaming."""
    from uuid import uuid4

    # Hydrate app (loads from resource_ids + hydrates Amethyst resources)
    app_obj = hydrate_app(app_id=app_id)
    run_id = str(uuid4())

    async def stream():
        messages = asyncio.Queue()

        def save_app_callback():
            # Save app state during execution (not resources)
            resource_ids = [r.id for r in app_obj.resources if r.id]
            app_to_save, now = downcast_to_app(app_obj, resource_ids)
            update_app(
                app_id,
                app_to_save.model_dump_json(
                    exclude={"memory": {"tasks": {"__all__": {"async_task"}}}}
                ),
                now,
            )

        engine = Engine(
            send_update=messages.put_nowait, save_app=save_app_callback, verbose=True
        )

        # Step 1: Plan (parse files, enrich resources)
        await engine.plan(app_obj)

        # Post-planning: Save all resources and update app
        resource_ids = save_resources(app_obj.resources)
        app_to_save, now = downcast_to_app(app_obj, resource_ids)
        update_app(
            app_id,
            app_to_save.model_dump_json(
                exclude={"memory": {"tasks": {"__all__": {"async_task"}}}}
            ),
            now,
        )

        # Step 2: Execute (run the planned app)
        task = asyncio.create_task(engine.run(app_obj, run_id))

        while not task.done() or not messages.empty():
            if not messages.empty():
                update = await messages.get()
                yield f"data: {json.dumps(update)}\n\n"
            await asyncio.sleep(0)

        await task

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/{app_id}/runs/{run_id}")
async def get_run_endpoint(app_id: str, run_id: str):
    """Get run by ID - returns the main task."""
    app_obj = hydrate_app(app_id)
    main_task = next(
        (t for t in app_obj.memory.tasks.values() if t.parent_task_id == run_id), None
    )
    if not main_task:
        raise HTTPException(status_code=404, detail="Run not found")

    return main_task.to_dict(include_ai_calls=True)
