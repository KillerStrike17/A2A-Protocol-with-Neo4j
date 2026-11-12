from datetime import datetime

from dotenv import load_dotenv
from google.adk.a2a.agent import RemoteA2aAgent
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.agent_tool import AgentTool

from .movie_tools import cancel_movie_plan, confirm_movie_plan, get_movie_plans

load_dotenv()

MODEL = "gemini-3.8-flash"

# Remote agents, reached over the A2A protocol. RemoteA2aAgent downloads each
# Agent Card the first time the agent is called, so the order you start the
# servers in doesn't matter.
movie_agent = RemoteA2aAgent(
    name="Movie_Agent",
    description="Recommends movies by genre, actor, director, year or keyword from a Neo4j movie graph.",
    agent_card="",  # TODO (Step 10): URL of the Movie Agent's Agent Card
    use_legacy=False,  # the Movie Agent is an ADK to_a2a() server, so use ADK's newer A2A integration
)

friend_agent = RemoteA2aAgent(
    name="Friend_Agent",
    description="Knows the friend's availability, favorite movie genres and the movies they have already watched.",
    agent_card="",  # TODO (Step 10): URL of the Friend Agent's Agent Card
)


def root_instruction(context: ReadonlyContext) -> str:
    return f"""
    **Role:** You are the Host Agent, an expert coordinator for movie recommendations and scheduling.
    Your job is to work with the `Movie_Agent` and the `Friend_Agent` to find a movie you and your
    friend can watch together, and a time to watch it.

    **Workflow for planning a movie:**
    1. Ask the `Friend_Agent`: "What genres of movies do you like and what movies have you already watched?"
       Only if the user explicitly asks about availability, scheduling or finding a time, ask instead:
       "Are you available to watch a movie this week? What are your favorite genres and what movies have you already watched?"
    2. Ask the `Movie_Agent` for recommendations in the friend's favorite genres,
       e.g. "Recommend 10 top-rated Comedy movies".
    3. Remove any recommended movie that appears in the friend's watched list.
    4. Present the remaining recommendations as bullet points with a short reason for each.
       If availability was checked, suggest matching time slots too.
    5. When the user picks a movie (and a time), save it with `confirm_movie_plan`
       (movie_title, date as YYYY-MM-DD, time as HH:MM) and reply with the plan ID.

    **Other tools:** use `get_movie_plans` to list saved plans and `cancel_movie_plan` to cancel one.

    **Rules:**
    *   Contact the agents yourself; don't ask the user for permission first.
    *   Only rely on what the tools and agents return; never make up movies or times.
    *   Keep answers concise and easy to read.

    **Today's date (YYYY-MM-DD):** {datetime.now().strftime("%Y-%m-%d")}
    """


root_agent = LlmAgent(
    model=MODEL,
    name="Host_Agent",
    description="Coordinates the Movie Agent and the Friend Agent to recommend and schedule a movie.",
    instruction=root_instruction,
    tools=[
        # TODO (Step 10): give the host the two remote agents as tools (AgentTool)
        confirm_movie_plan,
        get_movie_plans,
        cancel_movie_plan,
    ],
)
