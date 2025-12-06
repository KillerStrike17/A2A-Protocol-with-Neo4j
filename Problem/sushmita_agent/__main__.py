"""This file serves as the main entry point for the application.

It initializes the A2A server, defines the agent's capabilities,
and starts the server to handle incoming requests.
"""

import logging
import os

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent import SchedulingAgent
from agent_executor import SchedulingAgentExecutor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


def main():
    """Entry point for Sushmita's Scheduling Agent."""
    host = # TODO 
    port = # TODO
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            raise MissingAPIKeyError("GOOGLE_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=False)
        skill1 = AgentSkill(
            id="availability_checker",
            name="Availability Checker",
            description="Check my calendar to see when I'm available.",
            tags=["schedule", "availability", "calendar"],
            examples=[
                "Are you free tomorrow?",
                "When are you available this week?",
            ],
        )
        skill2 = AgentSkill(
            id="movie_preferences",
            name="Movie Preferences",
            description="Get my favorite movie genres and list of movies I've already watched.",
            tags=["movies", "preferences", "genres"],
            examples=[
                "What genres of movies do you like?",
                "What movies have you already watched?",
                "Are you available to watch a movie and what genres do you prefer?",
            ],
        )

        agent_host_url = os.getenv("HOST_OVERRIDE") or f"http://{host}:{port}/"
        agent_card = AgentCard(
            name=# TODO,
            description=(
               # TODO
            ),
            url=# TODO,
            version="1.0.0",
            defaultInputModes=SchedulingAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=SchedulingAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=# TODO,
            skills=# TODO,
            # skills=[skill1],
        )

        request_handler = DefaultRequestHandler(
            agent_executor=Z# TODO,
            task_store=InMemoryTaskStore(),
        )
        server = A2AStarletteApplication(
            agent_card=# TODO,
            http_handler=# TODO
        )

        uvicorn.run(server.build(), host=host, port=port)

    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
