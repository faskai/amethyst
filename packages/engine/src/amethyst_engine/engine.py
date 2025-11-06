"""Amethyst execution engine.

The Engine orchestrates parsing and execution of Amethyst code:
- Planner: Parses Amethyst syntax into execution plan
- Interpreter: Interprets code and executes MCP tools
- Memory: Tracks runtime state and results
"""

import logging
from typing import Callable

from dotenv import load_dotenv

from .app import App, Resource
from .hydrator import ResourceHydrator
from .interpreter import Interpreter
from .memory import Memory, TaskType

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

        await self.hydrator.hydrate_resources(list(app.resources.values()))

        for idx, amt_file in enumerate(app.files, 1):
            self.send_update(
                {"type": "progress", "message": f"Parsing file {idx}/{len(app.files)}"}
            )

            await self.planner.parse(amt_file, app)

            needs_oauth = [
                r for r in app.list_resources() if r.get("connection_status") == "needs_oauth"
            ]
            if needs_oauth:
                self.send_update({"type": "oauth_required", "resources": needs_oauth})
                return {"status": "oauth_required", "resources": needs_oauth}

            await self.execute(amt_file, app)
            self.send_update({"type": "progress", "message": f"Completed file {idx}"})

        self.send_update({"type": "progress", "message": "App execution completed"})
        return {"status": "completed", "memory": self.memory.get_context()}

    async def execute(self, amt_file, app: App):
        """Execute parsed file."""
        # Register functions as resources
        for func in amt_file.functions:
            app.resources[func["name"]] = Resource(
                type="function", name=func["name"], provider="amethyst"
            )

        mcp_tools = self.provider.get_execution_mcp_config(app.list_resources())
        interpreter = Interpreter(send_update=self.send_update, verbose=self.verbose)

        # Execute agents
        for agent_def in amt_file.amt_agents:
            await self._execute_agent(agent_def, app, interpreter, mcp_tools, amt_file)

    async def _execute_agent(self, agent_def: dict, app, interpreter, mcp_tools, amt_file):
        """Primitive #1: Execute agent block iteratively until completion."""
        self.send_update({"type": "progress", "message": f"Executing agent {agent_def['name']}"})
        agent_block = agent_def["block"]

        while True:
            task = await interpreter.interpret(
                agent_block, self.memory.get_context(), app.list_resources(), mcp_tools
            )
            self.memory.tasks[task.id] = task

            if task.task_type == TaskType.AMT_FUNCTION_CALL:
                task.result = await self._execute_function(
                    task.resource_name,
                    task.input.get("input", []),
                    app,
                    interpreter,
                    mcp_tools,
                    amt_file,
                )

            if task.task_type == TaskType.AMT_AGENT_CALL:
                self.send_update({"type": "result", "task": task.id, "result": task.result})
                return task

    async def _execute_function(
        self, func_name: str, input_data: list, app, interpreter, mcp_tools, amt_file
    ):
        """Primitive #2: Execute function blocks (sequence, repeat, parallel)."""
        func_def = next(f for f in amt_file.functions if f["name"] == func_name)
        results = []

        for block in func_def["blocks"]:
            if block["type"] == "sequence":
                block_results = await self._execute_statements(
                    block["statements"],
                    self.memory.get_context(),
                    app,
                    interpreter,
                    mcp_tools,
                    amt_file,
                )
                results.extend(block_results)

            elif block["type"] == "repeat":
                for idx, item in enumerate(input_data):
                    self.send_update(
                        {
                            "type": "progress",
                            "message": f"Processing item {idx + 1}/{len(input_data)}",
                        }
                    )
                    context = self.memory.get_context()
                    context["current_item"] = item

                    block_results = await self._execute_statements(
                        block["statements"], context, app, interpreter, mcp_tools, amt_file
                    )
                    results.extend(block_results)

        return results

    async def _execute_statements(
        self, statements: list, context: dict, app, interpreter, mcp_tools, amt_file
    ) -> list:
        """Primitive #4: Execute a list of statements."""
        results = []
        for statement in statements:
            task = await self._execute_statement(
                statement, context, app, interpreter, mcp_tools, amt_file
            )
            results.append(task.result)
        return results

    async def _execute_statement(
        self, statement: str, context: dict, app, interpreter, mcp_tools, amt_file
    ):
        """Primitive #3: Execute a single statement."""
        self.send_update({"type": "progress", "message": f"Executing statement {statement}"})
        task = await interpreter.interpret(statement, context, app.list_resources(), mcp_tools)
        self.memory.tasks[task.id] = task

        if task.task_type == TaskType.AMT_FUNCTION_CALL:
            task.result = await self._execute_function(
                task.resource_name,
                task.input.get("input", []),
                app,
                interpreter,
                mcp_tools,
                amt_file,
            )
        return task

    async def _await_tasks(self, task_ids):
        """Wait for async tasks."""
        for task_id in task_ids:
            task = self.memory.tasks[task_id]
            task.result = await task.async_task
