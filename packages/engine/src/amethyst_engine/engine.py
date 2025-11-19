"""Amethyst execution engine.

The Engine orchestrates parsing and execution of Amethyst code:
- Planner: Parses Amethyst syntax into execution plan
- Interpreter: Interprets code and executes MCP tools
- Memory: Tracks runtime state and results

Sample code:
```
function modify-docs
repeat for each in input
use google_docs to summarize the doc in 1 paragraph in a funny tone
end repeat
end function

function modify-docs-parallel
repeat for each in input
parallel use google_docs to summarize the doc in 1 paragraph in a funny tone
end repeat
wait
end function

agent write-doc
use google_docs to summarize content and write it into a new file called "Summary"
end agent

main agent bulk-summz
use google_docs to list the following 2 files: “GTA4” and “RDR2”
use modify-docs-parallel to get updated docs
Summarize the above in one paragraph
use write-doc to write to file
end agent
```
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from dotenv import load_dotenv

from .app import App
from .hydrator import ResourceHydrator
from .interpreter import Interpreter
from .memory import TaskExpanded, TaskType
from .planner import Planner
from .providers.pipedream import PipedreamProvider

logger = logging.getLogger(__name__)


@dataclass
class EngineContext:
    """Execution context passed through engine methods."""

    app: App
    mcp_tools: List[Dict[str, Any]] = field(default_factory=list)


class Engine:
    """Amethyst execution engine.

    Orchestrates compilation and execution:
    Planner → Interpreter → Executor
    """

    def __init__(
        self,
        send_update: Optional[Callable] = None,
        save_app: Optional[Callable] = None,
        verbose: bool = False,
    ):
        load_dotenv()

        self.verbose = verbose
        self.send_update = send_update or (lambda x: None)
        self.save_app = save_app or (lambda: None)
        self.provider = None
        self.planner = None
        self.hydrator = ResourceHydrator()

        if verbose:
            logging.basicConfig(level=logging.INFO)

    async def run(self, app: App, run_id: str) -> dict:
        """Run Amethyst app with multiple files."""

        # Initialize provider and planner with workspace_id from app
        self.provider = PipedreamProvider(workspace_id=app.workspaceId, verbose=self.verbose)
        self.planner = Planner(self.provider, send_update=self.send_update, verbose=self.verbose)

        for idx, amt_file in enumerate(app.files, 1):
            self.send_update(
                {"type": "progress", "message": f"Parsing file {idx}/{len(app.files)}"}
            )

            await self.planner.parse(amt_file, app)

            needs_oauth = [
                r for r in app.resources_expanded if r.connection_status == "needs_oauth"
            ]
            if needs_oauth:
                needs_oauth_dict = [r.model_dump() for r in needs_oauth]
                self.send_update({"type": "oauth_required", "resources": needs_oauth_dict})
                return {"status": "oauth_required", "resources": needs_oauth_dict}

            main_resource = next(r for r in app.resources_expanded if r.is_main)
            self.send_update(
                {"type": "progress", "message": f"Executing main: {main_resource.name}"}
            )

            context = EngineContext(
                app=app,
                mcp_tools=self.provider.get_execution_mcp_config(app.resources),
            )

            is_agent = main_resource.type == "amt_agent"
            task_type = TaskType.AMT_AGENT if is_agent else TaskType.AMT_FUNCTION
            main_task = await self._create_task(context, run_id, main_resource.name, task_type)
            await self._execute_task(main_task, context)

            self.send_update({"type": "progress", "message": f"Completed file {idx}"})
            self.save_app()

        self.send_update({"type": "progress", "message": "App execution completed"})

    async def _create_task(
        self,
        context: EngineContext,
        parent_task_id: str,
        resource_name: str,
        task_type: TaskType,
        input: Optional[List[Dict[str, Any]]] = None,
    ):
        task = TaskExpanded(
            parent_task_id=parent_task_id,
            resource_name=resource_name,
            task_type=task_type,
            input=input or [],
        )
        context.app.memory.tasks[task.id] = task
        self.send_update({"type": "task_created", "task": task.to_dict()})
        return task

    async def _execute_task(self, task: TaskExpanded, context: EngineContext):
        if task.task_type == TaskType.AMT_AGENT:
            await self._execute_agent(task, context)
        elif task.task_type == TaskType.AMT_FUNCTION:
            await self._execute_function(task, context)
        else:
            raise ValueError(f"Invalid task type: {task.task_type}")

    async def _interpret_and_execute(
        self,
        code: str,
        parent_task: TaskExpanded,
        context: EngineContext,
        interpreter: Interpreter,
    ):
        output, ai_call = await interpreter.interpret(
            code,
            context.app,
            context.mcp_tools,
            parent_task.id,
            parent_task.input,
        )

        # Update parent with ai_call
        parent_task.ai_calls.append(ai_call)
        self.send_update(
            {"type": "task_updated", "task": parent_task.to_dict(include_ai_calls=True)}
        )

        if output.result:
            # Completion - update parent result
            parent_task.result = output.result
            self.send_update(
                {"type": "task_updated", "task": parent_task.to_dict(include_ai_calls=True)}
            )
            return None

        # Task call - convert to TaskExpanded and execute
        child_task = TaskExpanded(**output.task.model_dump())
        context.app.memory.tasks[child_task.id] = child_task
        self.send_update({"type": "task_created", "task": child_task.to_dict()})
        await self._execute_task(child_task, context)

        return child_task

    async def _execute_agent(self, agent_task: TaskExpanded, context: EngineContext):
        interpreter: Interpreter = Interpreter(send_update=self.send_update, verbose=self.verbose)

        # Find agent definition
        agent_def = next(
            r for r in context.app.resources_expanded if r.name == agent_task.resource_name
        )

        # Loop until agent completes
        while True:
            child_task = await self._interpret_and_execute(
                agent_def.code, agent_task, context, interpreter
            )
            if child_task is None:  # Agent completed
                return agent_task

    async def _execute_function(self, func_task: TaskExpanded, context: EngineContext):
        """Execute function blocks (sequence, repeat, wait)."""
        func_def = next(
            r for r in context.app.resources_expanded if r.name == func_task.resource_name
        )
        input_data = func_task.input
        results = []

        for block in func_def.blocks:
            if block.type == "sequence":
                for stmt in block.statements:
                    stmt_task = await self._execute_statement(
                        stmt.text,
                        func_task,
                        context,
                        is_parallel=stmt.is_parallel,
                    )
                    if not stmt.is_parallel:
                        results.append(stmt_task.result)

            elif block.type == "repeat":
                for idx, item in enumerate(input_data):
                    self.send_update(
                        {
                            "type": "progress",
                            "message": f"Processing item {idx + 1}/{len(input_data)}",
                        }
                    )
                    for stmt in block.statements:
                        stmt_task = await self._execute_statement(
                            stmt.text,
                            func_task,
                            context,
                            input=item,
                            is_parallel=stmt.is_parallel,
                        )
                        if not stmt.is_parallel:
                            results.append(stmt_task.result)

            elif block.type == "wait":
                # Wait for all async tasks with same parent_task_id
                async_tasks = [
                    t.async_task
                    for t in context.app.memory.tasks.values()
                    if t.parent_task_id == func_task.id and t.async_task
                ]
                if async_tasks:
                    await asyncio.gather(*async_tasks)
                    # Collect results from async tasks
                    for t in context.app.memory.tasks.values():
                        if t.parent_task_id == func_task.id and t.async_task and t.result:
                            results.append(t.result)

        func_task.result = results
        self.send_update({"type": "task_updated", "task": func_task.to_dict(include_ai_calls=True)})

    async def _execute_statement(
        self,
        statement: str,
        parent_task: TaskExpanded,
        context: EngineContext,
        input: Optional[dict] = None,
        is_parallel: bool = False,
    ):
        """Execute statement - creates statement task and executes (sync or async)."""

        prefix = "parallel " if is_parallel else ""
        self.send_update(
            {"type": "progress", "message": f"Executing {prefix}statement {statement}"}
        )

        # Create statement task
        stmt_task = await self._create_task(
            context, parent_task.id, "", TaskType.STATEMENT, [input] if input else []
        )

        interpreter: Interpreter = Interpreter(send_update=self.send_update, verbose=self.verbose)

        # Execute statement
        async def execute():
            await self._interpret_and_execute(statement, stmt_task, context, interpreter)

        if is_parallel:
            stmt_task.async_task = asyncio.create_task(execute())
        else:
            await execute()

        return stmt_task
