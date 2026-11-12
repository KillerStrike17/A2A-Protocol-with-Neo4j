"""Entry point for the Friend Agent.

It defines the agent's A2A Agent Card and starts an A2A server
that handles incoming requests on port 10006.
"""

import logging
import os

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
from agent import SchedulingAgent
from agent_executor import SchedulingAgentExecutor
from dotenv import load_dotenv
from starlette.applications import Starlette

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = "localhost"
PORT = 0  # TODO (Step 9): the Friend Agent listens on port 10006


def main():
    """Starts the Friend Agent as an A2A server."""
    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY environment variable not set.")
        raise SystemExit(1)

    availability_skill = AgentSkill(
        id="availability_checker",
        name="Availability Checker",
        description="Check my calendar to see when I'm available.",
        tags=["schedule", "availability", "calendar"],
        examples=[
            "Are you free tomorrow?",
            "When are you available this week?",
        ],
    )
    preferences_skill = AgentSkill(
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

    agent_url = os.getenv("HOST_OVERRIDE") or f"http://{HOST}:{PORT}/"
    # TODO (Step 9): build the Agent Card.
    agent_card = AgentCard(
        name="",  # TODO
        description="",  # TODO
        version="1.0.0",
        supported_interfaces=[],  # TODO: use agent_url
        default_input_modes=SchedulingAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=SchedulingAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=AgentCapabilities(),  # TODO
        skills=[],  # TODO
    )

    request_handler = DefaultRequestHandler(
        agent_executor=SchedulingAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )
    # Serve the Agent Card at /.well-known/agent-card.json and JSON-RPC at /.
    # TODO (Step 9): add the Agent Card route and the JSON-RPC route.
    app = Starlette(routes=[])
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
