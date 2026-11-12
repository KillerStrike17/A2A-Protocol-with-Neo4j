import asyncio

from a2a.helpers import new_task_from_user_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import UnsupportedOperationError
from agent import SchedulingAgent


class SchedulingAgentExecutor(AgentExecutor):
    """A2A executor that runs the CrewAI scheduling and movie preferences agent."""

    def __init__(self):
        self.agent = SchedulingAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Runs the crew for one A2A request and publishes the result as an artifact."""
        if not context.task_id or not context.context_id:
            raise ValueError("RequestContext must have task_id and context_id")
        if not context.message:
            raise ValueError("RequestContext must have a message")

        # 1. Register a new task (state: submitted) the first time we see it.
        if not context.current_task:
            await event_queue.enqueue_event(new_task_from_user_message(context.message))

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.start_work()

        # 2. CrewAI's kickoff() is synchronous, so run it in a worker thread to
        #    keep the server's event loop responsive.
        query = context.get_user_input()
        result = ""  # TODO (Step 9): run self.agent.invoke(query) in a worker thread

        # 3. Return the answer as an artifact and mark the task completed.
        # TODO (Step 9): add `result` as an artifact, then mark the task completed.

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Cancellation is not supported by this agent."""
        raise UnsupportedOperationError()
