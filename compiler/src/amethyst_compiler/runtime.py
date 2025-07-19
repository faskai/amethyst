import logging
from typing import Optional
from uuid import uuid4
import httpx

from . import amethyst_types
from . import parser as amethyst_parser
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
)


class AmethystCompiler:
    """Main compiler for Amethyst language."""
    
    def __init__(self):
        self.parser = amethyst_parser.AmethystParser()
        self.registry = amethyst_types.ResourceRegistry()
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def register_resource(self, resource: amethyst_types.ResourceDefinition) -> None:
        """Register a resource in the compiler's registry."""
        self.registry.register_resource(resource)
        self.logger.info(f"Registered {resource.resource_type.value} '{resource.name}' in registry")
    
    async def compile_and_execute(self, amethyst_code: str) -> str:
        """Compile and execute Amethyst code."""
        # Parse the agent
        agent_def = self.parser.parse_agent(amethyst_code)
        if not agent_def:
            return "Error: Could not parse agent definition"
        
        # Parse invoke calls
        invoke_calls = self.parser.parse_invoke_calls(amethyst_code)
        
        result = f"Agent '{agent_def.name}' created with instructions: {agent_def.instructions}\n"
        result += f"Invoke calls found: {invoke_calls}\n"
        
        # Execute A2A communication for each invoke call
        for call in invoke_calls:
            a2a_result = await self.execute_a2a_communication(call, agent_def.instructions)
            result += f"A2A communication with @{call}: {a2a_result}\n"
        
        return result
    
    async def execute_a2a_communication(self, resource_name: str, prompt: str) -> str:
        """Execute agent-to-agent communication using A2A SDK."""
        try:
            # Look up the resource in the registry
            resource = self.registry.get_resource(resource_name)
            if not resource:
                return f"Error: Resource '{resource_name}' not found in registry"
            
            if resource.resource_type != amethyst_types.ResourceType.AGENT:
                return f"Error: Resource '{resource_name}' is not an agent"
            
            agent_def = resource.definition
            if not agent_def.url:
                return f"Error: Agent '{resource_name}' has no URL configured"
            
            base_url = agent_def.url
            
            async with httpx.AsyncClient() as httpx_client:
                # Initialize A2ACardResolver
                resolver = A2ACardResolver(
                    httpx_client=httpx_client,
                    base_url=base_url,
                )
                
                # Fetch agent card
                agent_card = await resolver.get_agent_card()
                self.logger.info(f"Successfully fetched agent card for {resource_name}")
                
                # Initialize A2A client
                client = A2AClient(
                    httpx_client=httpx_client, 
                    agent_card=agent_card
                )
                
                # Send the full agent prompt
                send_message_payload = {
                    'message': {
                        'role': 'user',
                        'parts': [
                            {'kind': 'text', 'text': prompt}
                        ],
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
            return f"Error in A2A communication: {str(e)}" 