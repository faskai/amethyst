import re
from typing import Dict, List, Optional
from . import amethyst_types


class AmethystParser:
    """Simple parser for Amethyst syntax."""
    
    def __init__(self):
        self.agent_pattern = re.compile(r'agent\s+(\w+)', re.IGNORECASE)
        self.end_pattern = re.compile(r'end\s+agent', re.IGNORECASE)
        self.invoke_pattern = re.compile(r'@(\w+)', re.IGNORECASE)
    
    def parse_agent(self, content: str) -> Optional[amethyst_types.AgentDefinition]:
        """Parse an agent definition from Amethyst code."""
        lines = content.strip().split('\n')
        
        # Find agent name
        agent_match = None
        for line in lines:
            agent_match = self.agent_pattern.search(line)
            if agent_match:
                break
        
        if not agent_match:
            return None
        
        agent_name = agent_match.group(1)
        
        # Find instructions (everything between agent and end)
        instructions = []
        in_agent = False
        
        for line in lines:
            line = line.strip()
            
            # Check if we're starting the agent
            if self.agent_pattern.search(line):
                in_agent = True
                continue
            
            # Check if we're ending the agent
            if self.end_pattern.search(line):
                break
            
            # If we're inside the agent, collect instructions
            if in_agent and line:
                instructions.append(line)
        
        # Join instructions
        instruction_text = ' '.join(instructions)
        
        return amethyst_types.AgentDefinition(
            name=agent_name,
            instructions=instruction_text
        )
    
    def parse_invoke_calls(self, content: str) -> List[str]:
        """Parse all invoke calls from the content."""
        return self.invoke_pattern.findall(content) 