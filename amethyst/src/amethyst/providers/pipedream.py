"""Pipedream MCP provider."""

import os
from amethyst.planner import ExternalResource
from pipedream import Pipedream
from .provider import ToolProvider
from typing import List


class PipedreamProvider(ToolProvider):
    """Pipedream provider implementation."""
    
    def __init__(self, verbose: bool = False):
        self.user_id = os.getenv("PIPEDREAM_EXTERNAL_USER_ID", "default_user")
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
            "require_approval": "never"
        }
    
    def get_execution_mcp_config(self, available_resources: list) -> list[dict]:
        """Get MCP configs for specific apps."""
        return [{
            "type": "mcp",
            "server_label": r["name"],
            "server_url": "https://remote.mcp.pipedream.net",
            "headers": {
                "Authorization": f"Bearer {self.access_token}",
                "x-pd-project-id": self.project_id,
                "x-pd-environment": self.project_environment,
                "x-pd-external-user-id": self.user_id,
                "x-pd-app-slug": r["name"],
                "x-pd-tool-mode": "sub-agent",
            },
            "require_approval": "never"
        } for r in available_resources if r["provider"] == "pipedream"]
    
    def enrich_resources(self, resources: List[ExternalResource]) -> list[dict]:
        """Enrich discovered resources with Pipedream connection status and auth URLs."""
        enriched = []
        connect_link_base = None

        for resource in resources:
            if resource.provider == "external":
                enriched_resource = resource.dict()
                enriched_resource["provider"] = "pipedream"
                enriched_resource["type"] = "tool"

                accounts = list(self.pd.accounts.list(external_user_id=self.user_id, app=resource.name))

                if accounts:
                    enriched_resource["connection_status"] = "connected"
                    enriched_resource["auth_url"] = None
                else:
                    if not connect_link_base:
                        connect_link_base = self.pd.tokens.create(external_user_id=self.user_id).connect_link_url
                    
                    enriched_resource["connection_status"] = "needs_oauth"
                    enriched_resource["auth_url"] = f"{connect_link_base}&app={resource.name}"

                enriched.append(enriched_resource)

        return enriched

