"""Resource API routes."""

import os

from amethyst_engine.app import Resource
from fastapi import APIRouter, HTTPException, Request
from pipedream import Pipedream
from resources_dao import (
    create_resource,
    delete_resource,
    get_resource,
    list_resources,
)
from resources_dao import (
    search_resources as search_resources_db,
)

router = APIRouter(prefix="/resources", tags=["resources"])

# Lazy Pipedream client initialization
_pd_client = None


def get_pd_client():
    """Get or create Pipedream client (lazy initialization)."""
    global _pd_client
    if _pd_client is None:
        _pd_client = Pipedream(
            project_id=os.getenv("PIPEDREAM_PROJECT_ID"),
            project_environment=os.getenv(
                "PIPEDREAM_PROJECT_ENVIRONMENT", "production"
            ),
            client_id=os.getenv("PIPEDREAM_CLIENT_ID"),
            client_secret=os.getenv("PIPEDREAM_CLIENT_SECRET"),
        )
    return _pd_client


@router.get("/")
async def list_resources_endpoint():
    """List all resources."""
    return list_resources()


@router.get("/search")
async def search_resources_endpoint(q: str = ""):
    """Search resources from Pipedream and saved resources, dedupe by ID (prefer Pipedream)."""
    resources_map = {}

    # Search saved resources at DB level (efficient)
    saved_resources = search_resources_db(q)
    for resource in saved_resources:
        resources_map[resource.get("id")] = Resource(
            id=resource.get("id"),
            name=resource.get("name"),
            type=resource.get("type"),
            provider=resource.get("provider"),
            img_url=resource.get("img_url"),
        )

    # Get Pipedream apps (will override saved resources with same ID)
    try:
        pd_client = get_pd_client()
        apps = pd_client.apps.list(q=q)
        for app in apps:
            resources_map[app.name_slug] = Resource(
                id=app.name_slug,
                name=app.name,
                type="tool",
                provider="pipedream",
                img_url=app.img_src if hasattr(app, "img_src") else None,
            )
    except Exception:
        # If Pipedream fails, continue with saved resources
        pass

    return [r.model_dump() for r in resources_map.values()]


@router.post("/")
async def create_resource_endpoint(request: Request):
    """Create or update resource."""
    body = await request.json()
    resource = Resource(**body)
    resource_id = resource.id
    if not resource_id:
        raise HTTPException(status_code=400, detail="Resource ID is required")
    create_resource(resource_id, resource.model_dump())
    return {"id": resource_id}


@router.get("/{resource_id}")
async def get_resource_endpoint(resource_id: str):
    """Get resource by ID."""
    json_obj = get_resource(resource_id)
    if not json_obj:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"id": resource_id, **json_obj}


@router.delete("/{resource_id}")
async def delete_resource_endpoint(resource_id: str):
    """Delete resource by ID."""
    delete_resource(resource_id)
    return {"message": "Resource deleted"}
