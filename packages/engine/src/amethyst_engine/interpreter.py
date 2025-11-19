"""Amethyst code interpretation."""

import json
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel

from .app import App
from .llm import LLM, AiCall
from .memory import Task, TaskType
from .prompts import AMT_INTERPRETER_INSTRUCTIONS


class InterpreterOutput(BaseModel):
    """Output from interpreter - either a task to execute or a result."""

    task: Task | None = None
    result: str | None = None


CALL_RESOURCE_TOOL = {
    "type": "function",
    "name": "call_amt_resource",
    "description": "Call an Amethyst function or agent resource",
    "parameters": {
        "type": "object",
        "properties": {
            "resource_name": {
                "type": "string",
                "description": "Name of the resource to call",
            },
            "task_type": {
                "type": "string",
                "enum": ["amt_function", "amt_agent"],
                "description": "Type of resource",
            },
            "input": {
                "type": "array",
                "items": {"type": "object", "additionalProperties": True},
                "description": (
                    "Array of input objects. Always provide this field, "
                    "use empty array [] if no input needed"
                ),
                "default": [],
            },
        },
        "required": ["resource_name", "task_type", "input"],
    },
}


class Interpreter:
    """Interprets Amethyst code."""

    def __init__(self, send_update: Callable, verbose: bool = False):
        self.llm = LLM(send_update=send_update, verbose=verbose)
        self.verbose = verbose
        self.send_update = send_update
        self.history = []

    def _get_attr(self, item, key):
        """Get attribute from object or dict."""
        return getattr(item, key, None) or (item.get(key) if isinstance(item, dict) else None)

    def _should_keep_reasoning(self, output_list: list, current_idx: int) -> bool:
        """Check if reasoning item should be kept based on following item."""
        if current_idx + 1 >= len(output_list):
            return False

        next_item = output_list[current_idx + 1]
        next_type = self._get_attr(next_item, "type")

        # Keep reasoning if followed by mcp_call or computer_call
        return next_type in ["mcp_call", "computer_call"]

    def _serialize_for_history(self, output: Any, output_list: list = None, idx: int = 0) -> Any:
        """Serialize output for history, handling special cases."""
        output_type = self._get_attr(output, "type")

        # Handle reasoning: keep only if followed by mcp_call or computer_call
        if output_type == "reasoning":
            if output_list and not self._should_keep_reasoning(output_list, idx):
                return None
            return output

        # Serialize function_call with only API-accepted fields
        if output_type == "function_call":
            serialized = {
                "type": "function_call",
                "call_id": str(self._get_attr(output, "call_id")),
                "name": str(self._get_attr(output, "name")),
                "arguments": str(self._get_attr(output, "arguments")),
            }
            return serialized

        # Return other outputs as-is (MCP calls, messages, etc.)
        return output

    def _update_function_call_outputs(self, app: App):
        """Update or add function_call_output for all function_calls (handles parallel calls)."""
        if not self.history:
            return

        processed_outputs = set()

        for i, item in enumerate(self.history):
            if (
                self._get_attr(item, "type") == "function_call"
                and self._get_attr(item, "name") == "call_amt_resource"
            ):
                call_id = str(self._get_attr(item, "call_id"))
                if call_id in processed_outputs:
                    continue

                task_id = f"task-{call_id}"
                task = app.memory.tasks.get(task_id)
                output_value = (
                    json.dumps(task.result) if task and task.result else "Async, pending..."
                )

                # Check if function_call_output already exists after this call and update it
                found_output = False
                for j in range(i + 1, len(self.history)):
                    next_item = self.history[j]
                    if (
                        self._get_attr(next_item, "type") == "function_call_output"
                        and str(self._get_attr(next_item, "call_id")) == call_id
                    ):
                        if isinstance(next_item, dict):
                            next_item["output"] = output_value
                        found_output = True
                        processed_outputs.add(call_id)
                        break

                if not found_output:
                    self.history.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": output_value,
                        }
                    )
                    processed_outputs.add(call_id)

    async def interpret(
        self,
        code: str,
        app: App,
        mcp_tools: List[Dict[str, Any]],
        parent_task_id: str,
        input: Optional[Any] = None,
    ) -> tuple[InterpreterOutput, AiCall]:
        """Interpret code and return (output, ai_call)."""

        self._update_function_call_outputs(app)

        sys_msg = {
            "role": "system",
            "content": f"""{AMT_INTERPRETER_INSTRUCTIONS}

Resources:
{json.dumps([r.model_dump() for r in app.resources], indent=2)}

Code:
{code}

Input:
{json.dumps(input, indent=2) if input else "None"}
""",
        }

        all_tools = mcp_tools + [CALL_RESOURCE_TOOL]

        response, ai_call = await self.llm.stream(
            messages=[sys_msg, *self.history],
            tools=all_tools,
        )

        # Add output list to history (serialize function_calls, conditionally keep reasoning)
        output_list = getattr(response, "output", [])
        serialized_outputs = [
            self._serialize_for_history(output, output_list, idx)
            for idx, output in enumerate(output_list)
        ]
        self.history.extend([item for item in serialized_outputs if item is not None])

        # Parse output to determine return value
        function_call = None
        assistant_message = None

        for output in output_list:
            if (
                getattr(output, "type", None) == "function_call"
                and getattr(output, "name", None) == "call_amt_resource"
            ):
                function_call = output
            elif getattr(output, "type", None) == "message":
                assistant_message = output

        # Return task or result
        if function_call:
            args = json.loads(str(function_call.arguments))
            task = Task(
                id=f"task-{function_call.call_id}",
                parent_task_id=parent_task_id,
                resource_name=args["resource_name"],
                task_type=TaskType(args["task_type"]),
                input=args.get("input", []),
            )
            return InterpreterOutput(task=task), ai_call
        else:
            result_text = ""
            if assistant_message and (content := getattr(assistant_message, "content", None)):
                text_parts = []
                for item in content:
                    if text := getattr(item, "text", None):
                        text_parts.append(str(text))
                result_text = " ".join(text_parts)
            return InterpreterOutput(result=result_text), ai_call
