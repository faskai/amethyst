"""Amethyst code interpretation.

Interprets AFL code to determine next execution steps.
"""

import openai
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from .memory import Task, Step, TaskType, StepType
from .syntax import AFL_INTERPRETER_INSTRUCTIONS
from dataclasses import asdict


class Interpreter:
    """Interprets AFL code to determine execution steps."""
    
    def __init__(self, verbose: bool = False):
        load_dotenv()
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.verbose = verbose
        self.conversation_history = []
        
    async def interpret(
        self,
        instructions: str,
        memory: str,
        current_position: int,
        available_resources: List[Dict[str, str]],
        mcp_tools: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Interpret AFL+ASL and execute external tools via MCP."""
        resources_json = json.dumps(available_resources, indent=2)
        tools = mcp_tools.copy()
        
        tools.extend([
            {
                "type": "function",
                "name": "create_task",
                "description": "Create task for delegation (A2A calls, Amethyst tool calls)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": f"Create an id in this format: task-<line-number>-<name-of-the-task>"},
                        "resource_name": {"type": "string", "description": "Resource name to call"},
                        "task_type": {"type": "string", "enum": ["agent_call", "tool_call"]},
                        "parameters": {"type": "object", "description": "Tool call parameters"},
                        "instructions": {"type": "string", "description": "Agent call instructions in natural language"},
                        "is_async": {"type": "boolean"},
                        "next_position": {"type": "integer", "description": "Next line to execute"}
                    },
                    "required": ["id", "resource_name", "task_type", "next_position"]
                }
            },
            {
                "type": "function", 
                "name": "create_step",
                "description": "Create control flow step (await). Provide the task ids to await.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "step_type": {"type": "string", "enum": ["await"]},
                        "task_ids": {"type": "array", "items": {"type": "string"}},
                        "next_position": {"type": "integer", "description": "Next line to execute"}
                    },
                    "required": ["step_type", "task_ids", "next_position"]
                }
            },
            {
                "type": "function",
                "name": "complete_execution",   
                "description": "Done - set next_position to -1",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "next_position": {"type": "integer", "description": "Set to -1 when done"}
                    },
                    "required": ["next_position"]
                }
            }
        ])
        
        numbered_code = '\n'.join([
            f"{'>>>' if i == current_position else '   '} {i:3d}: {line}"
            for i, line in enumerate(instructions.split('\n'))
        ])
        
        input = [
            {"role": "system", "content": f"{AFL_INTERPRETER_INSTRUCTIONS}\n\nResources:\n{resources_json}"},
            *self.conversation_history,
            {"role": "user", "content": f"Code (>>> marks current line):\n{numbered_code}\n\nMemory:\n{memory}"}
        ]

        response = self.client.responses.create(model="gpt-5-mini", tools=tools, input=input)
        self.conversation_history.extend(response.output)
        
        tasks, steps = [], []
        next_position = -1
        
        for item in response.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)
                next_position = args["next_position"]
                
                if item.name == "create_task":
                    tasks.append(Task(
                        id=args["id"],
                        resource_name=args["resource_name"],
                        task_type=TaskType(args["task_type"]),
                        parameters=args.get("parameters", {}),
                        is_async=args.get("is_async", False)
                    ))
                elif item.name == "create_step":
                    steps.append(Step(
                        step_type=StepType(args["step_type"]),
                        task_ids=args["task_ids"]
                    ))
                
                self.conversation_history.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({"status": "success"})
                })

            if self.verbose:
                print(f"\n🤖 INTERPRETER: {json.dumps(item.model_dump(), indent=2)}")

        return {"tasks": tasks, "steps": steps, "next_position": next_position}