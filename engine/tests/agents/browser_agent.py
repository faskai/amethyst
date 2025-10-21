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


class BrowserAgentExecutor(AgentExecutor):
    """Browser agent executor that simulates web browsing and booking actions."""
    
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

        # Generate dummy browsing and booking results
        browse_data = """
🌐 **Web Browse & Booking Actions Completed:**

**✅ PARKING RESERVATION CONFIRMED:**
**SpotHero - Canlis Restaurant Area**
- Location: 200 Aurora Ave N (2 blocks from restaurant)
- Date: Today
- Time: 6:30 PM - 10:00 PM
- Rate: $12.00 for 3.5 hours
- Confirmation #: SH-AUR-8847-P
- Space #: A-24

**✅ ADDITIONAL BOOKINGS:**
**Uber Ride Scheduled**
- Pickup: Your location → Canlis Restaurant
- Time: 6:45 PM
- Estimated fare: $18-24
- Driver will be assigned 10 minutes before pickup

**Browsed & Found:**
- ✅ Restaurant reviews on Yelp (4.8/5 stars)
- ✅ Menu preview and dietary options confirmed
- ✅ Weather forecast checked (light rain expected)
- ✅ Traffic conditions analyzed (25 min drive time)

**Security Actions:**
- ✅ Saved parking confirmation to calendar
- ✅ Added restaurant address to GPS favorites
- ✅ Set reminder 30 minutes before departure

All bookings confirmed and ready for your dinner! 🎉
        """

        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                append=False,
                contextId=task.contextId,
                taskId=task.id,
                lastChunk=True,
                artifact=new_text_artifact(
                    name='browsing_booking_results',
                    description='Web browsing and booking confirmations for reservations and parking.',
                    text=browse_data,
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


def get_browser_config():
    """Get configuration for browser agent."""
    skill = AgentSkill(
        id='web_browse_book',
        name='Web browsing and booking',
        description='Browse websites, find information, and make bookings/reservations',
        tags=['web browsing', 'booking', 'automation', 'research'],
        examples=['book parking near restaurant', 'find and book uber ride', 'research venue information'],
    )

    return {
        "name": "Browser Agent",
        "description": "General web browsing agent that can navigate websites and perform booking actions",
        "skills": [skill],
        "executor_class": BrowserAgentExecutor
    }
