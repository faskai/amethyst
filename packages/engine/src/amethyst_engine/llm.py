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
        text_format: Optional[Type[BaseModel]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        model: str = "gpt-5-mini",
    ) -> tuple[Any, AiCall]:
        """Stream LLM response and return (final_result, ai_call)."""
        # Serialize input messages (may contain OpenAI response objects)
        serialized_input = [
            self._serialize_output(msg) if not isinstance(msg, dict) else msg for msg in messages
        ]
        ai_call = AiCall(input_messages=serialized_input)
        params = {"model": model, "tools": tools or [], "input": messages}
        if text_format:
            params["text_format"] = text_format

        async with self.client.responses.stream(**params) as stream:
            if self.send_update:
                async for event in stream:
                    if delta := getattr(event, "delta", None):
                        self.send_update({"type": "ai_intermediate_output", "delta": delta})

            result = await stream.get_final_response()

            ai_call.intermediate_outputs = [
                self._serialize_output(output) for output in getattr(result, "output", [])
            ]

            return result, ai_call

    def _serialize_output(self, output: Any) -> dict:
        """Extract main string fields from output."""
        result = {}

        string_fields = [
            "type",
            "name",
            "output",
            "error",
            "status",
            "id",
            "role",
            "server_label",
            "arguments",
            "summary",
        ]
        for field in string_fields:
            if val := getattr(output, field, None):
                result[field] = str(val)

        if content := getattr(output, "content", None):
            text_parts = [str(item.text) for item in content]
            if text_parts:
                result["content"] = " ".join(text_parts)

        return result
