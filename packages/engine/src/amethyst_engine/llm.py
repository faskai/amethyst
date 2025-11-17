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
        """Convert output object to JSON-serializable dict."""
        if hasattr(output, "model_dump"):
            # Pydantic models
            return output.model_dump()
        elif hasattr(output, "__dict__"):
            # Plain objects - recursively serialize
            result = {}
            for key, value in output.__dict__.items():
                if key.startswith("_"):
                    continue
                try:
                    # Test if value is JSON serializable
                    import json

                    json.dumps(value)
                    result[key] = value
                except (TypeError, ValueError):
                    # Not serializable, convert to string representation
                    result[key] = str(value)
            return result
        else:
            return {"value": str(output)}
