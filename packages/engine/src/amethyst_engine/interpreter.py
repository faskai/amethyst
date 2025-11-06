"""Amethyst code interpretation."""

import json
from typing import Any, Callable, Dict, List

from pydantic import BaseModel, Field

from .llm import LLM
from .memory import Task, TaskType
from .syntax import AMT_INTERPRETER_INSTRUCTIONS


class InterpreterOutput(BaseModel):
    model_config = {"extra": "forbid"}

    task_type: str
    resource_name: str = ""
    result: str | None = None
    input: str | None = Field(
        default=None, description="JSON string containing list of input objects for function call"
    )


class Interpreter:
    """Interprets Amethyst code."""

    def __init__(self, send_update: Callable, verbose: bool = False):
        self.llm = LLM(send_update=send_update, verbose=verbose)
        self.verbose = verbose
        self.send_update = send_update
        self.messages = []

    async def interpret(
        self,
        code: str,
        memory: dict,
        resources: List[Dict[str, str]],
        mcp_tools: List[Dict[str, Any]],
    ) -> Task:
        """Interpret code and return task."""
        user_msg = {
            "role": "user",
            "content": f"""{AMT_INTERPRETER_INSTRUCTIONS}

Resources:
{json.dumps(resources, indent=2)}

Code:
{code}

Task results:
{json.dumps(memory, indent=2)}""",
        }

        response = await self.llm.stream(
            messages=[user_msg, *self.messages],
            text_format=InterpreterOutput,
            tools=mcp_tools,
        )
        parsed = response.output_parsed

        if parsed.task_type == TaskType.AMT_FUNCTION_CALL:
            self.messages.append({"role": "assistant", "content": json.dumps(parsed.model_dump())})

        return Task(
            resource_name=parsed.resource_name,
            task_type=TaskType(parsed.task_type),
            input={"input": json.loads(parsed.input)} if parsed.input else {},
            result=parsed.result,
        )
