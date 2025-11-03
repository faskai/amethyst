"""Amethyst code interpretation.

Interprets Amethyst code to determine next execution steps.
"""

import json
from typing import Any, Callable, Dict, List

from pydantic import BaseModel

from .llm import LLM
from .memory import Step, StepType, Task, TaskType
from .syntax import AMT_INTERPRETER_INSTRUCTIONS


class ResponseModel(BaseModel):
    task_id: str
    result: str


class Interpreter:
    """Interprets Amethyst code to determine execution steps."""

    def __init__(self, send_update: Callable, verbose: bool = False):
        self.llm = LLM(send_update=send_update, verbose=verbose)
        self.verbose = verbose
        self.send_update = send_update

    async def interpret(
        self,
        instructions: str,
        memory: dict,
        available_resources: List[Dict[str, str]],
        mcp_tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Interpret Amethyst code and execute external tools via MCP."""
        resources_json = json.dumps(available_resources, indent=2)
        tools = mcp_tools.copy()

        tools.extend(
            [
                # {
                #     "type": "function",
                #     "name": "create_task",
                #     "description": (
                #         "Create task for delegation (A2A calls, Amethyst tool calls)."
                #         "Only applicable when the corresponding resource provider is 'amethyst'."
                #     ),
                #     "parameters": {
                #         "type": "object",
                #         "properties": {
                #             "id": {
                #                 "type": "string",
                #                 "description": (
                #                     "Create an id in this format: "
                #                     "task-<line-number>-<name-of-the-task>"
                #                 ),
                #             },
                #             "resource_name": {
                #                 "type": "string",
                #                 "description": "Resource name to call",
                #             },
                #             "task_type": {
                #                 "type": "string",
                #                 "enum": ["agent_call", "tool_call"],
                #             },
                #             "parameters": {
                #                 "type": "object",
                #                 "description": "Tool call parameters",
                #             },
                #             "instructions": {
                #                 "type": "string",
                #                 "description": "Agent call instructions in natural language",
                #             },
                #             "is_async": {"type": "boolean"},
                #             "next_position": {
                #                 "type": "integer",
                #                 "description": "Next line to execute",
                #             },
                #         },
                #         "required": [
                #             "id",
                #             "resource_name",
                #             "task_type",
                #             "next_position",
                #         ],
                #     },
                # },
                # {
                #     "type": "function",
                #     "name": "create_step",
                #     "description": (
                #         "Create control flow step (await). Provide the task ids to await."
                #     ),
                #     "parameters": {
                #         "type": "object",
                #         "properties": {
                #             "step_type": {"type": "string", "enum": ["await"]},
                #             "task_ids": {"type": "array", "items": {"type": "string"}},
                #             "next_position": {
                #                 "type": "integer",
                #                 "description": "Next line to execute",
                #             },
                #         },
                #         "required": ["step_type", "task_ids", "next_position"],
                #     },
                # },
            ]
        )

        memory_json = json.dumps(memory, indent=2)
        messages = [
            {
                "role": "system",
                "content": (f"{AMT_INTERPRETER_INSTRUCTIONS}\n\nResources:\n{resources_json}"),
            },
            {
                "role": "user",
                "content": (f"Memory:\n{memory_json}\n\nCode:\n{instructions}"),
            },
        ]

        tasks, steps = [], []

        final_response = await self.llm.stream(
            messages=messages, text_format=ResponseModel, tools=tools
        )

        # Handle parsed response (no function calls)
        if hasattr(final_response, "output_parsed"):
            parsed = final_response.output_parsed
            tasks.append(
                Task(
                    id=parsed.task_id,
                    resource_name="",
                    task_type=TaskType.AMT_AGENT_RESULT,
                    is_async=False,
                    result=parsed.result,
                )
            )

        # Handle function calls
        for item in final_response.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)
                if item.name == "create_task":
                    tasks.append(
                        Task(
                            id=args["id"],
                            resource_name=args["resource_name"],
                            task_type=TaskType(args["task_type"]),
                            parameters=args.get("parameters", {}),
                            is_async=args.get("is_async", False),
                        )
                    )
                elif item.name == "create_step":
                    steps.append(
                        Step(
                            step_type=StepType(args["step_type"]),
                            task_ids=args["task_ids"],
                        )
                    )

        return {
            "tasks": tasks,
            "steps": steps,
        }
