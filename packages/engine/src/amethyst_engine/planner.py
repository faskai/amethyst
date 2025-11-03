"""Amethyst code compilation.

Compiles casual language to Amethyst syntax using AI.
"""

import json
from typing import Callable, List, Literal

from pydantic import BaseModel

from .llm import LLM
from .syntax import AMT_COMPILER_INSTRUCTIONS


class ExternalResource(BaseModel):
    type: Literal["a2a_agent", "tool"]
    provider: Literal["amethyst", "external"]
    name: str


class PlanResult(BaseModel):
    amt_agents: List[str] = []
    resources: List[ExternalResource] = []


class Planner:
    """Compiles casual language to Amethyst syntax using AI."""

    def __init__(self, provider, send_update: Callable, verbose: bool = False):
        self.provider = provider
        self.llm = LLM(send_update=send_update, verbose=verbose)
        self.send_update = send_update
        self.verbose = verbose

    async def compile(self, acl: str, available_resources: list, memory: dict) -> dict:
        """Compile casual language to Amethyst syntax using AI."""

        prompt = f"""
Memory:
{json.dumps(memory)}

Instructions:
{AMT_COMPILER_INSTRUCTIONS}

Resources:
{json.dumps(available_resources)}

Casual language input:
{acl}"""

        messages = [{"role": "user", "content": prompt}]
        tools = [self.provider.get_discovery_mcp_config()]

        response = await self.llm.stream(messages=messages, text_format=PlanResult, tools=tools)

        if self.verbose:
            print(f"\n🤖 PLANNER: {json.dumps(response.output_parsed.model_dump(), indent=2)}\n")

        enriched_resources = self.provider.enrich_resources(response.output_parsed.resources)
        return {"amt_agents": response.output_parsed.amt_agents, "resources": enriched_resources}
