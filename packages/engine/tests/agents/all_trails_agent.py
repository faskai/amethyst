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


class AllTrailsAgentExecutor(AgentExecutor):
    """AllTrails agent executor that returns dummy hiking trail data."""
    
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

        # Generate dummy trail data based on query
        trails_data = """
🥾 **Great Hiking Trails Found:**

**1. Rattlesnake Ledge Trail**
- Distance: 4.0 miles roundtrip
- Elevation gain: 1,160 ft
- Difficulty: Moderate
- Features: Amazing views of Rattlesnake Lake and Mount Si
- Trailhead: Rattlesnake Lake Recreation Area

**2. Mount Pilchuck Trail** 
- Distance: 5.4 miles roundtrip
- Elevation gain: 2,300 ft
- Difficulty: Moderate to Hard
- Features: Fire tower lookout with 360° views
- Trailhead: Mount Pilchuck State Park

**3. Lake 22 Trail**
- Distance: 5.4 miles roundtrip  
- Elevation gain: 1,350 ft
- Difficulty: Moderate
- Features: Beautiful alpine lake surrounded by peaks
- Trailhead: Mountain Loop Highway

All trails are under 10K elevation and offer spectacular views as requested!
        """

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                append=False,
                contextId=task.contextId,
                taskId=task.id,
                lastChunk=True,
                artifact=new_text_artifact(
                    name='trail_recommendations',
                    description='Hiking trail recommendations with views under 10K elevation.',
                    text=trails_data,
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


def get_all_trails_config():
    """Get configuration for all trails agent."""
    skill = AgentSkill(
        id='find_trails',
        name='Find hiking trails',
        description='Find hiking trails based on criteria like distance, elevation, views',
        tags=['hiking', 'trails', 'outdoor', 'nature'],
        examples=['find hikes under 10K with views', 'good trails nearby', 'moderate hikes with lookouts'],
    )

    return {
        "name": "AllTrails Agent",
        "description": "Find and recommend hiking trails based on your criteria",
        "skills": [skill],
        "executor_class": AllTrailsAgentExecutor
    }
