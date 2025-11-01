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


class OpenTableAgentExecutor(AgentExecutor):
    """OpenTable agent executor that returns dummy restaurant booking data."""
    
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

        # Generate dummy restaurant booking data
        restaurant_data = """
🍽️ **Waterfront Restaurants with PNW Food Found & Booked:**

**✅ RESERVATION CONFIRMED:**
**Canlis Restaurant**
- Cuisine: Pacific Northwest Fine Dining
- Location: 2576 Aurora Ave N, Seattle (Waterfront views)
- Reservation: Today 7:00 PM for 2 people
- Confirmation #: CNL-2024-8847
- Features: Stunning lake views, locally sourced ingredients
- Specialties: Wild salmon, Dungeness crab, seasonal vegetables

**Alternative Options Found:**
**The Walrus & The Carpenter** (Ballard)
- Oyster bar with waterfront location
- Available: 8:30 PM

**Westward** (Lake Union)
- Modern American with PNW influences  
- Available: 6:00 PM or 9:00 PM

**Matt's in the Market** (Pike Place)
- Farm-to-table with Sound views
- Available: 5:30 PM

Weather looks rainy today - perfect for cozy waterfront dining! 🌧️
        """

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                append=False,
                contextId=task.contextId,
                taskId=task.id,
                lastChunk=True,
                artifact=new_text_artifact(
                    name='restaurant_booking',
                    description='Restaurant search and booking confirmation for waterfront PNW dining.',
                    text=restaurant_data,
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


def get_open_table_config():
    """Get configuration for open table agent."""
    skill = AgentSkill(
        id='book_restaurant',
        name='Find and book restaurants',
        description='Search for restaurants by cuisine, location, and make reservations',
        tags=['dining', 'restaurant', 'booking', 'reservation', 'food'],
        examples=['book waterfront restaurant with PNW food', 'find good seafood restaurant', 'make dinner reservation'],
    )

    return {
        "name": "OpenTable Agent",
        "description": "Find and book restaurant reservations based on your preferences",
        "skills": [skill],
        "executor_class": OpenTableAgentExecutor
    }
