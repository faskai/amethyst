"""Pipedream MCP provider."""

import os
from typing import List

from pipedream import Pipedream

from ..app import Resource, ResourceExpanded
from .provider import ToolProvider


class PipedreamProvider(ToolProvider):
    """Pipedream provider implementation."""

    def __init__(self, workspace_id: str, verbose: bool = False):
        self.user_id = workspace_id
        self.project_id = os.getenv("PIPEDREAM_PROJECT_ID")
        self.project_environment = os.getenv("PIPEDREAM_PROJECT_ENVIRONMENT")
        self.client_id = os.getenv("PIPEDREAM_CLIENT_ID")
        self.client_secret = os.getenv("PIPEDREAM_CLIENT_SECRET")
        self.verbose = verbose

        self.pd = Pipedream(
            project_id=self.project_id,
            project_environment=self.project_environment,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self.access_token = self.pd.raw_access_token

    def get_discovery_mcp_config(self) -> dict:
        """Get MCP config with app discovery."""
        return {
            "type": "mcp",
            "server_label": "pipedream",
            "server_url": "https://remote.mcp.pipedream.net",
            "headers": {
                "Authorization": f"Bearer {self.access_token}",
                "x-pd-project-id": self.project_id,
                "x-pd-environment": self.project_environment,
                "x-pd-external-user-id": self.user_id,
                "x-pd-app-discovery": "true",
                "x-pd-tool-mode": "full-config",
            },
            "require_approval": "never",
        }

    def get_execution_mcp_config(self, available_resources: List[Resource]) -> list[dict]:
        """Get MCP configs for specific apps."""
        return [
            {
                "type": "mcp",
                "server_label": r.key,
                "server_url": "https://remote.mcp.pipedream.net",
                "headers": {
                    "Authorization": f"Bearer {self.access_token}",
                    "x-pd-project-id": self.project_id,
                    "x-pd-environment": self.project_environment,
                    "x-pd-external-user-id": self.user_id,
                    "x-pd-app-slug": r.key,
                    "x-pd-tool-mode": "sub-agent",
                },
                "require_approval": "never",
            }
            for r in available_resources
            if r.provider == "pipedream"
        ]

    def enrich_resources(self, resources: List[ResourceExpanded]):
        """Enrich ResourceExpanded objects in place with Pipedream connection status and auth URLs."""
        connect_link_base = None
        for resource in resources:
            if resource.provider == "pipedream" and resource.key:
                accounts = list(
                    self.pd.accounts.list(external_user_id=self.user_id, app=resource.key)
                )
                if accounts:
                    resource.connection_status = "connected"
                    resource.auth_url = None
                else:
                    if not connect_link_base:
                        connect_link_base = self.pd.tokens.create(
                            external_user_id=self.user_id
                        ).connect_link_url
                    resource.connection_status = "needs_oauth"
                    resource.auth_url = f"{connect_link_base}&app={resource.key}"
