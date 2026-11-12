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

    skill = AgentSkill(
        id="movie_recommendations",
        name="Movie Recommendations",
        description="Recommends movies based on genre, actor, director, year, or keywords using a Neo4j movie graph.",
        tags=["movies", "recommendations", "entertainment"],
        examples=[
            "Recommend some action movies",
            "What movies has Tom Hanks acted in?",
            "Show me movies from 1999",
            "Find movies about space",
        ],
    )
    agent_card = AgentCard(
        name="Movie Agent",
        description="An intelligent movie recommendation agent that helps you discover movies based on your preferences using a Neo4j database.",
        version="1.0.0",
        supported_interfaces=[
            AgentInterface(
                url=f"http://{HOST}:{PORT}/",
                protocol_binding="JSONRPC",
                protocol_version="1.0",
            )
        ],
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # to_a2a wraps the ADK agent in an A2A server: it serves the Agent Card at
    # /.well-known/agent-card.json and handles JSON-RPC requests at /.
    app = to_a2a(create_agent(), host=HOST, port=PORT, agent_card=agent_card)
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
