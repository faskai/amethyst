"""Amethyst code parsing."""

import json
from typing import Callable, List, Literal, Optional

from pydantic import BaseModel, ConfigDict

from .app import AmtBlock, Resource, ResourceExpanded, Statement
from .llm import LLM
from .prompts import AMT_PARSER_INSTRUCTIONS


class ParsedStatement(BaseModel):
    """Simple statement for LLM output."""

    model_config = ConfigDict(extra="forbid")

    text: str
    is_parallel: bool = False


class ParsedBlock(BaseModel):
    """Simple block for LLM output."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["sequence", "repeat", "wait"]
    statements: List[ParsedStatement]


class ParsedResource(BaseModel):
    """Simple resource for LLM output."""

    model_config = ConfigDict(extra="forbid")

    name: str
    type: Literal["amt_agent", "amt_function"]
    is_main: bool
    code: Optional[str] = None
    blocks: List[ParsedBlock]


class ParseResult(BaseModel):
    """Parser output containing parsed resources."""

    model_config = ConfigDict(extra="forbid")

    resources: List[ParsedResource]


class Planner:
    """Parses AMT syntax into execution plan."""

    def __init__(self, provider, send_update: Callable, verbose: bool = False):
        self.provider = provider
        self.llm = LLM(send_update=send_update, verbose=verbose)
        self.send_update = send_update
        self.verbose = verbose

    async def parse(self, amt_file, app):
        """Parse AMT code into app.resources_expanded."""

        prompt = f"{AMT_PARSER_INSTRUCTIONS}\n\nAMT Code:\n{amt_file.content}"
        messages = [{"role": "user", "content": prompt}]
        response, ai_call = await self.llm.stream(
            messages=messages, text_format=ParseResult, tools=[]
        )

        if self.verbose:
            print(f"\n🤖 PARSER: {json.dumps(response.output_parsed.model_dump(), indent=2)}\n")

        # Map ParsedResource to ResourceExpanded
        app.resources_expanded = []
        for parsed_res in response.output_parsed.resources:
            # Convert ParsedBlock to AmtBlock
            blocks = [
                AmtBlock(
                    type=block.type,
                    statements=[
                        Statement(text=stmt.text, is_parallel=stmt.is_parallel)
                        for stmt in block.statements
                    ],
                )
                for block in parsed_res.blocks
            ]

            # Create ResourceExpanded
            resource_expanded = ResourceExpanded(
                name=parsed_res.name,
                type=parsed_res.type,
                provider="amethyst",
                is_main=parsed_res.is_main,
                code=parsed_res.code,
                blocks=blocks,
            )
            app.resources_expanded.append(resource_expanded)

        # Enrich with provider-specific metadata (e.g., Pipedream connection status)
        self.provider.enrich_resources(app.resources_expanded)

        # Create lightweight Resource objects for non-main resources (sent to interpreter LLM)
        for res in app.resources_expanded:
            if not res.is_main:
                app.resources.append(
                    Resource(type=res.type, name=res.name, provider=res.provider, key=res.key)
                )
