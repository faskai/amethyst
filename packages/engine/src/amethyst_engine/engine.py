"""Amethyst execution engine.

The Engine orchestrates the compilation and execution of Amethyst code:
- Planner: Compiles casual language to Amethyst syntax
- Interpreter: Interprets Amethyst code and determines execution steps
- Executor: Executes tasks (agent calls, tool calls)
- Memory: Tracks runtime state and results
"""

import asyncio
import logging
from typing import Callable

from dotenv import load_dotenv

from .app import App, Resource
from .executor import call_agent, call_tool
from .hydrator import ResourceHydrator
from .interpreter import Interpreter
from .memory import Memory, StepType, TaskType

logger = logging.getLogger(__name__)


class Engine:
    """Amethyst execution engine.

    Orchestrates compilation and execution:
    Planner → Interpreter → Executor
    """

    def __init__(self, send_update: Callable, verbose: bool = False):
        load_dotenv()

        self.memory = Memory()
        self.verbose = verbose
        self.send_update = send_update

        from .providers.pipedream import PipedreamProvider

        self.provider = PipedreamProvider(verbose=verbose)

        from .planner import Planner

        self.planner = Planner(self.provider, send_update=send_update, verbose=verbose)
        self.hydrator = ResourceHydrator()

        if verbose:
            logging.basicConfig(level=logging.INFO)

    async def run(self, app: App) -> dict:
        """Run Amethyst app with multiple files."""
        self.send_update({"type": "progress", "message": "Starting app"})

        await self.hydrator.hydrate_resources(list(app.resources.values()))

        for idx, amt_file in enumerate(app.files, 1):
            self.send_update(
                {"type": "progress", "message": f"Processing file {idx}/{len(app.files)}"}
            )

            compiled_plan = await self.planner.compile(
                amt_file.content, app.list_resources(), self.memory.get_context()
            )
            self.memory.files.append({"content": {"amt_agents": compiled_plan["amt_agents"]}})

            for r in compiled_plan["resources"]:
                resource = Resource(**r)
                app.resources[resource.name] = resource

            needs_oauth = [
                r for r in compiled_plan["resources"] if r.get("connection_status") == "needs_oauth"
            ]
            if needs_oauth:
                self.send_update({"type": "oauth_required", "resources": needs_oauth})
                return {"status": "oauth_required", "resources": needs_oauth}

            await self.execute(self.memory.files[-1], app)
            self.send_update({"type": "progress", "message": f"Completed file {idx}"})

        self.send_update({"type": "progress", "message": "App execution completed"})
        return {"status": "completed", "memory": self.memory.get_context()}

    async def execute(self, file: dict, app: App) -> dict:
        """Execute compiled AFL code."""
        mcp_tools = self.provider.get_execution_mcp_config(app.list_resources())
        interpreter = Interpreter(send_update=self.send_update, verbose=self.verbose)

        for amt_agent in file["content"]["amt_agents"]:
            self.send_update({"type": "progress", "message": f"Interpreting agent: {amt_agent}"})
            execution_plan = await interpreter.interpret(
                instructions=amt_agent,
                memory=self.memory.get_context(),
                available_resources=app.list_resources(),
                mcp_tools=mcp_tools,
            )

            for task in execution_plan["tasks"]:
                self.memory.tasks[task.id] = task
                self.send_update(
                    {
                        "type": "progress",
                        "message": f"Task: {task.task_type} - resource: {task.resource_name}",
                    }
                )
                if task.task_type == TaskType.AGENT_CALL:
                    coro = call_agent(task.resource_name, task.parameters, app.resources)
                elif task.task_type == TaskType.TOOL_CALL:
                    coro = call_tool(task.resource_name, task.parameters, app.resources)
                else:
                    continue

                if task.is_async:
                    task.async_task = asyncio.create_task(coro)
                else:
                    task.result = await coro
                    self.send_update(
                        {"type": "progress", "message": f"Completed: {task.resource_name}"}
                    )

            for step in execution_plan["steps"]:
                if step.step_type == StepType.AWAIT:
                    self.send_update({"type": "progress", "message": "Waiting for async tasks"})
                    await self._await_tasks(step.task_ids)
                    self.memory.steps.append(step)

        return self.memory.get_context()

    async def _await_tasks(self, task_ids):
        """Wait for tasks and store results."""
        for task_id in task_ids:
            task = self.memory.tasks[task_id]
            task.result = await task.async_task
