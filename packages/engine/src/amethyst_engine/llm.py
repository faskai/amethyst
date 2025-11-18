"""OpenAI LLM interface."""

import os
from typing import Any, Callable, Dict, List, Optional, Type

import openai
from dotenv import load_dotenv
from pydantic import BaseModel

from .memory import AiCall


class LLM:
    """Consistent interface for OpenAI LLM calls."""

    def __init__(self, send_update: Optional[Callable] = None, verbose: bool = False):
        load_dotenv()
        self.client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.send_update = send_update
        self.verbose = verbose

    async def stream(
        self,
        messages: List[Dict[str, str]],
        text_format: Type[BaseModel],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-5-mini",
    ) -> tuple[Any, AiCall]:
        """Stream LLM response and return (final_result, ai_call)."""
        ai_call = AiCall(input_messages=messages.copy())

        async with self.client.responses.stream(
            model=model, tools=tools or [], input=messages, text_format=text_format
        ) as stream:
            if self.send_update:
                async for event in stream:
                    # Send only delta to UI ephemerally
                    if hasattr(event, "delta"):
                        self.send_update({"type": "ai_intermediate_output", "delta": event.delta})

            result = await stream.get_final_response()

            # Capture intermediate outputs array as JSON-serializable dicts
            if hasattr(result, "output") and result.output:
                ai_call.intermediate_outputs = [
                    self._serialize_output(output) for output in result.output
                ]

            return result, ai_call

    def _serialize_output(self, output: Any) -> dict:
        """Extract minimal common fields showing main content."""
        result = {}

        # type is universal across all output types
        if hasattr(output, "type"):
            result["type"] = str(output.type)

        # Extract main content based on type
        # Messages and reasoning have content array
        if hasattr(output, "content") and output.content:
            # Extract text from content array
            text_parts = []
            for item in output.content:
                if hasattr(item, "text"):
                    text_parts.append(str(item.text))
                elif isinstance(item, str):
                    text_parts.append(item)
            if text_parts:
                result["content"] = " ".join(text_parts)

        # Tool calls have name
        if hasattr(output, "name"):
            result["name"] = str(output.name)

        # Tool results have output
        if hasattr(output, "output"):
            output_val = output.output
            if isinstance(output_val, str):
                result["output"] = output_val[:200]  # Truncate long outputs
            elif output_val is not None:
                result["output"] = str(output_val)[:200]

        # Errors
        if hasattr(output, "error"):
            error = output.error
            if isinstance(error, dict):
                result["error"] = error.get("message", str(error))
            elif error:
                result["error"] = str(error)

        return result
