"""Task execution.

Executes agent calls and tool calls.
"""

from typing import Any, Dict, List
from uuid import uuid4

import httpx
import openai

# A2A imports
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

from . import types


async def call_tool(
    tool_name: str, parameters: Dict[str, Any], registry: types.ResourceRegistry
) -> str:
    """Execute tool call."""
    resource = registry.get_resource(tool_name)

    async with httpx.AsyncClient() as client:
        response = await client.post(resource.url, json=parameters)
        response.raise_for_status()
        result = response.json()
        return result.get("result", str(result))


async def call_agent(
    agent_name: str, parameters: Dict[str, Any], registry: types.ResourceRegistry
) -> str:
    """Execute agent call."""
    resource = registry.get_resource(agent_name)

    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=resource.url,
        )

        agent_card = await resolver.get_agent_card()

        client = A2AClient(httpx_client=httpx_client, agent_card=agent_card)

        send_message_payload = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": parameters["prompt"]}],
                "messageId": uuid4().hex,
            },
        }

        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)
        return response.model_dump(mode="json", exclude_none=True)


async def execute_asl_block(
    asl_block: str, mcp_tools: List[Dict[str, Any]], memory_context: str
) -> str:
    """Execute ASL agent block using OpenAI + MCP (one-shot agentic execution)."""
    client = openai.OpenAI()

    response = client.responses.create(
        model="gpt-4o",
        tools=mcp_tools,
        input=f"""Execute this agent:

{asl_block}

Previous context:
{memory_context}""",
    )

    return response.output_text
