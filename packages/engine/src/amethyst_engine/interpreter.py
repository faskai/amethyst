"""Amethyst code interpretation."""

import json
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

from .llm import LLM, AiCall
from .prompts import AMT_INTERPRETER_INSTRUCTIONS


class InterpreterTask(BaseModel):
    """Task to be created (function or agent call)."""

    resource_name: str
    task_type: str = Field(default="amt_function", description="amt_function or amt_agent")
    input: str | None = Field(
        default=None, description="JSON string containing list of input objects for function call"
    )


class InterpreterResult(BaseModel):
    """Completion result for agent or statement."""

    result: str


class InterpreterOutput(BaseModel):
    """Output from interpreter - either a task to execute or a result."""

    model_config = {"extra": "forbid"}

    task: InterpreterTask | None = None
    result: InterpreterResult | None = None


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
        resources: List[Dict],
        mcp_tools: List[Dict[str, Any]],
        parent_task_id: str,
        input: Optional[Any] = None,
    ) -> tuple[InterpreterOutput, AiCall]:
        """Interpret code and return (output, ai_call)."""

        user_msg_1 = {
            "role": "user",
            "content": f"""{AMT_INTERPRETER_INSTRUCTIONS}

Resources:
{json.dumps(resources, indent=2)}
""",
        }

        user_msg_2 = {
            "role": "user",
            "content": f"""Context:
{json.dumps(memory, indent=2)}

Code:
{code}

Input:
{json.dumps(input, indent=2) if input else "None"}
""",
        }

        response, ai_call = await self.llm.stream(
            messages=[user_msg_1, *self.messages, user_msg_2],
            text_format=InterpreterOutput,
            tools=mcp_tools,
        )
        parsed = response.output_parsed

        if parsed.task:
            # Function call - add to conversation history
            self.messages.append({"role": "assistant", "content": json.dumps(parsed.model_dump())})

        return parsed, ai_call
