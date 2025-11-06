"""OpenAI LLM interface."""

import os
from typing import Any, Callable, Dict, List, Optional, Type

import openai
from dotenv import load_dotenv
from pydantic import BaseModel


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
    ) -> Any:
        """Stream LLM response and return final result."""
        async with self.client.responses.stream(
            model=model, tools=tools or [], input=messages, text_format=text_format
        ) as stream:
            if self.send_update:
                async for event in stream:
                    content = f": {event.delta}" if hasattr(event, "delta") else ""
                    self.send_update(
                        {"type": "progress_details", "message": f"{event.type}{content}"}
                    )

            return await stream.get_final_response()
