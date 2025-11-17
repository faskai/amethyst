"""Amethyst code parsing."""

import json
from typing import Callable, List

from pydantic import BaseModel

from .llm import LLM
from .syntax import AMT_PARSER_INSTRUCTIONS


class AgentDef(BaseModel):
    name: str
    block: str


class FunctionBlock(BaseModel):
    type: str
    statements: List[str]


class FunctionDef(BaseModel):
    name: str
    blocks: List[FunctionBlock]


class ParseResult(BaseModel):
    amt_agents: List[AgentDef] = []
    functions: List[FunctionDef] = []


class Planner:
    """Parses AMT syntax into execution plan."""

    def __init__(self, provider, send_update: Callable, verbose: bool = False):
        self.provider = provider
        self.llm = LLM(send_update=send_update, verbose=verbose)
        self.send_update = send_update
        self.verbose = verbose

    async def parse(self, amt_file, app):
        """Parse AMT code and update file in place."""

        prompt = f"{AMT_PARSER_INSTRUCTIONS}\n\nAMT Code:\n{amt_file.content}"
        messages = [{"role": "user", "content": prompt}]
        response = await self.llm.stream(messages=messages, text_format=ParseResult, tools=[])

        if self.verbose:
            print(f"\n🤖 PARSER: {json.dumps(response.output_parsed.model_dump(), indent=2)}\n")

        amt_file.__dict__.update(response.output_parsed.model_dump())
        self.provider.enrich_resources(list(app.resources.values()))
