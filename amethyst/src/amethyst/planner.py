"""Amethyst code compilation.

Compiles ACL (casual) to AFL (formal) using AI.
"""

import openai
from dataclasses import asdict
from pydantic import BaseModel
from typing import Dict, List, Optional, Literal
import json

from .syntax import AFL_COMPILER_INSTRUCTIONS, AFL_SYNTAX_SPEC


class ExternalResource(BaseModel):
    type: Literal["agent", "tool"]    
    provider: Literal["amethyst", "external"]    
    name: str


class PlanResult(BaseModel):
    code: str
    resources: List[ExternalResource] = []


class Planner:
    """Compiles ACL (casual language) to AFL (formal language)."""
    
    def __init__(self, provider, verbose: bool = False):
        self.provider = provider
        self.openai = openai.OpenAI()
        self.verbose = verbose
    
    def compile(self, acl: str, available_resources: list) -> dict:
        """Compile ACL to AFL+ASL (.amt format) code."""
        prompt = f"""Instructions:
{AFL_COMPILER_INSTRUCTIONS}

Resources:
{json.dumps(available_resources)}

ACL Input:
{acl}"""
        
        response = self.openai.responses.parse(
            model="gpt-5-mini",
            tools=[self.provider.get_discovery_mcp_config()],
            input=[{"role": "user", "content": prompt}],
            text_format=PlanResult
        )

        if self.verbose:
            print(f"\n🤖 PLANNER: {json.dumps(response.output_parsed.model_dump(), indent=2)}")

        enriched_resources = self.provider.enrich_resources(response.output_parsed.resources)
        return {"code": response.output_parsed.code, "resources": enriched_resources}
