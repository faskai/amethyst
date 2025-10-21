"""Task execution functions."""

import httpx
from uuid import uuid4
from typing import Dict, Any

# A2A imports
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

from . import types


async def call_tool(tool_name: str, parameters: Dict[str, Any], registry: types.ResourceRegistry) -> str:
    """Call MCP tool."""
    
    resource = registry.get_resource(tool_name)
    if not resource or resource.resource_type != types.ResourceType.TOOL:
        return f"Tool {tool_name} not found"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                resource.definition.url,
                json=parameters,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', str(result))
            else:
                return f"HTTP {response.status_code}"
                
    except Exception as e:
        return f"Error: {e}"


async def call_agent(agent_name: str, parameters: Dict[str, Any], registry: types.ResourceRegistry) -> str:
    """Call A2A agent."""
    
    resource = registry.get_resource(agent_name)
    if not resource or resource.resource_type != types.ResourceType.AGENT:
        return f"Agent {agent_name} not found"
        
    try:
        prompt = parameters.get('prompt', 'Execute task')
        
        async with httpx.AsyncClient() as httpx_client:
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=resource.definition.url,
            )
            
            agent_card = await resolver.get_agent_card()
            
            client = A2AClient(
                httpx_client=httpx_client, 
                agent_card=agent_card
            )
            
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': prompt}],
                    'messageId': uuid4().hex,
                },
            }
            
            request = SendMessageRequest(
                id=str(uuid4()), 
                params=MessageSendParams(**send_message_payload)
            )
            
            response = await client.send_message(request)
            return f"Success: {response.model_dump(mode='json', exclude_none=True)}"
            
    except Exception as e:
        return f"Error: {e}"
