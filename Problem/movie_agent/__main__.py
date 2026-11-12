import logging
import os

import uvicorn
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
from agent import create_agent
from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOST = "localhost"
PORT = 10005


def main():
    """Starts the Movie Agent as an A2A server."""
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").upper() != "TRUE" and not os.getenv(
        "GOOGLE_API_KEY"
    ):
        logger.error(
            "GOOGLE_API_KEY is not set and GOOGLE_GENAI_USE_VERTEXAI is not TRUE."
        )
        raise SystemExit(1)

    # TODO (Step 8): describe what the agent can do.
    skill = AgentSkill(
        id="",  # TODO
        name="",  # TODO
        description="",  # TODO
        tags=[],  # TODO
        examples=[],  # TODO
    )
    # TODO (Step 8): build the Agent Card that other agents will read.
    agent_card = AgentCard(
        name="",  # TODO
        description="",  # TODO
        version="1.0.0",
        supported_interfaces=[],  # TODO: where and how to reach the agent
        default_input_modes=[],  # TODO
        default_output_modes=[],  # TODO
        capabilities=AgentCapabilities(),  # TODO
        skills=[],  # TODO
    )

    # to_a2a wraps the ADK agent in an A2A server: it serves the Agent Card at
    # /.well-known/agent-card.json and handles JSON-RPC requests at /.
    app = None  # TODO (Step 8): wrap create_agent() with to_a2a(...)
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
