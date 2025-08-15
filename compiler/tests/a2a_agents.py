#!/usr/bin/env python3
"""A2A Agent management for Amethyst testing."""

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard
from typing import Dict

# Import agent configurations
from agents import AGENT_CONFIGS


class A2AAgentManager:
    """Manager for A2A agent setup and configuration."""
    
    def __init__(self, port: int = 9998):
        self.port = port
        self.agents = {}
    
    def setup_agents(self, app) -> Dict[str, A2AStarletteApplication]:
        """Setup all A2A agents and mount them to the FastAPI app."""
        
        # Get agent configurations from the agents package
        agent_configs = {name: config_func() for name, config_func in AGENT_CONFIGS.items()}
        
        # Create A2A applications for each agent
        for agent_name, config in agent_configs.items():
            
            agent_card = AgentCard(
                name=config["name"],
                description=config["description"],
                url=f'http://localhost:{self.port}/agents/{agent_name}/',
                version='1.0.0',
                defaultInputModes=['text'],
                defaultOutputModes=['text'],
                capabilities=AgentCapabilities(streaming=True),
                skills=config["skills"],
                supportsAuthenticatedExtendedCard=False,
            )
            
            request_handler = DefaultRequestHandler(
                agent_executor=config["executor_class"](),
                task_store=InMemoryTaskStore(),
            )
            
            a2a_app = A2AStarletteApplication(
                agent_card=agent_card,
                http_handler=request_handler,
            )
            
            # Mount each agent at its own path
            app.mount(f"/agents/{agent_name}", a2a_app.build())
            self.agents[agent_name] = a2a_app
        
        return self.agents
    
    def get_agent_names(self) -> list[str]:
        """Get list of available agent names."""
        return list(self.agents.keys())
    
    def get_agent_configs(self) -> Dict[str, dict]:
        """Get all agent configurations."""
        return {name: config_func() for name, config_func in AGENT_CONFIGS.items()}
