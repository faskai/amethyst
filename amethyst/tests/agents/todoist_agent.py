from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    AgentSkill,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_task, new_text_artifact


class TodoistAgentExecutor(AgentExecutor):
    """Todoist agent executor that manages dummy todo lists."""
    
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = context.get_user_input()
        task = context.current_task

        if not context.message:
            raise Exception('No message provided')

        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        # Generate dummy todo list data
        todo_data = """
📝 **Todo List Created for Day Trip:**

**✅ PREPARATION CHECKLIST CREATED:**

**🎒 Things to Pack:**
- [ ] Hiking boots (waterproof)
- [ ] Rain jacket & umbrella ☔
- [ ] Water bottles (2L total)
- [ ] Trail snacks (energy bars, nuts)
- [ ] First aid kit (basic)
- [ ] Phone charger/power bank
- [ ] Camera for scenic views 📷
- [ ] Cash for parking/tips

**📋 Things to Do Before Leaving:**
- [ ] Check trail conditions online
- [ ] Download offline maps
- [ ] Tell someone your hiking plan
- [ ] Check restaurant dress code
- [ ] Confirm parking reservation
- [ ] Set GPS waypoints
- [ ] Check weather one more time

**🚗 Day of Logistics:**
- [ ] 5:30 PM - Start getting ready
- [ ] 6:00 PM - Leave for parking spot
- [ ] 6:30 PM - Park car, walk to restaurant
- [ ] 7:00 PM - Dinner at Canlis
- [ ] 9:30 PM - Head home

**📱 Reminders Set:**
- ⏰ 5:00 PM - "Start getting ready for dinner"
- ⏰ 6:45 PM - "Uber arrives in 10 minutes"

All tasks organized and synced to your Todoist app! 🎯
        """

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                append=False,
                contextId=task.contextId,
                taskId=task.id,
                lastChunk=True,
                artifact=new_text_artifact(
                    name='todo_checklist',
                    description='Organized todo list and checklist for day trip planning.',
                    text=todo_data,
                ),
            )
        )
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                status=TaskStatus(state=TaskState.completed),
                final=True,
                contextId=task.contextId,
                taskId=task.id,
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')


def get_todoist_config():
    """Get configuration for todoist agent."""
    skill = AgentSkill(
        id='manage_todos',
        name='Manage todo lists and tasks',
        description='Create, organize, and manage todo lists, checklists, and reminders',
        tags=['productivity', 'tasks', 'planning', 'organization', 'reminders'],
        examples=['create packing checklist', 'plan todo items', 'organize day schedule'],
    )

    return {
        "name": "Todoist Agent",
        "description": "Task management agent that creates and organizes todo lists and reminders",
        "skills": [skill],
        "executor_class": TodoistAgentExecutor
    }
