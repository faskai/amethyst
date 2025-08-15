"""OpenAI GPT-5 orchestrator agent."""

import openai
import os
import json
from typing import List, Dict, Any, Union
from dotenv import load_dotenv
from .memory import Task, Step, TaskType, StepType


class Orchestrator:
    """LLM powered orchestrator."""
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = openai.OpenAI(api_key=api_key)
        
    async def plan_execution(
        self,
        instructions: str,
        memory_summary: str,
        current_position: int,
        available_resources: List[str]
    ) -> Dict[str, Any]:
        """Plan next execution using GPT-5 tool calling."""
        
        lines = [line.strip() for line in instructions.split('\n') if line.strip()]
        context_lines = lines[current_position:current_position+5] if current_position < len(lines) else []
        
        # Build tools
        tools = [r for r in available_resources if r.startswith('tool:')]
        agents = [r for r in available_resources if r.startswith('agent:')]
        
        function_tools = []
        
        # Add task creation function
        function_tools.append({
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a task to call an agent or tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Unique task ID"},
                        "resource_name": {"type": "string", "description": "Resource name like @get_weather"},
                        "task_type": {"type": "string", "enum": ["tool_call", "agent_call"]},
                        "parameters": {"type": "object", "description": "Parameters for the call"},
                        "is_async": {"type": "boolean", "description": "Whether to run async"}
                    },
                    "required": ["id", "resource_name", "task_type"]
                }
            }
        })
        
        # Add step creation function
        function_tools.append({
            "type": "function", 
            "function": {
                "name": "create_step",
                "description": "Create an await step",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "step_type": {"type": "string", "enum": ["await"]},
                        "task_ids": {"type": "array", "items": {"type": "string"}, "description": "Task IDs to await"}
                    },
                    "required": ["step_type", "task_ids"]
                }
            }
        })
        
        # Add completion function
        function_tools.append({
            "type": "function",
            "function": {
                "name": "complete_execution",
                "description": "Mark execution as complete",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "next_position": {"type": "integer", "description": "Next line to process, -1 if done"}
                    },
                    "required": ["next_position"]
                }
            }
        })
        
        tool_list = ', '.join([f"@{t[5:]}" for t in tools]) if tools else "None"
        agent_list = ', '.join([f"@{a[6:]}" for a in agents]) if agents else "None"
        
        system_prompt = f"""You are an orchestrator for the Amethyst execution engine.

Available Resources:
- Tools: {tool_list} 
- Agents: {agent_list}

Analyze the instructions and create tasks/steps to execute. Use the provided functions.
"""

        user_prompt = f"""
INSTRUCTIONS: {instructions}
MEMORY: {memory_summary}
CURRENT POSITION: {current_position}  
NEXT LINES: {context_lines}

What should execute next?"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                tools=function_tools,
                tool_choice="auto"
            )
            
            tasks = []
            steps = []
            next_position = current_position + 1
            
            # Process tool calls
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    if func_name == "create_task":
                        task = Task(
                            id=args["id"],
                            resource_name=args["resource_name"],
                            task_type=TaskType(args["task_type"]),
                            parameters=args.get("parameters", {}),
                            is_async=args.get("is_async", False)
                        )
                        tasks.append(task)
                    elif func_name == "create_step":
                        step = Step(
                            step_type=StepType(args["step_type"]),
                            task_ids=args["task_ids"]
                        )
                        steps.append(step)
                    elif func_name == "complete_execution":
                        next_position = args["next_position"]
            
            return {
                "tasks": tasks,
                "steps": steps,
                "next_position": next_position
            }
            
        except Exception as e:
            print(f"Orchestrator error: {e}")
            return {"tasks": [], "steps": [], "next_position": -1}
