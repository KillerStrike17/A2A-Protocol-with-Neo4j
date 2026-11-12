# A2A Protocol with Neo4j

A hands-on project in which three AI agents work together over the open
[Agent2Agent (A2A) protocol](https://a2a-protocol.org) to plan a movie night with a friend.
It's built to teach **A2A**, **interoperability between agent frameworks** (Google ADK + CrewAI),
**MCP** (the official Neo4j MCP server), **Google ADK**, **Gemini** and **Neo4j**.

| Agent | Framework | Port | What it does |
|---|---|---|---|
| **Movie Agent** | Google ADK + Neo4j + MCP | `10005` | Recommends movies with Cypher tools and answers open graph questions through the Neo4j MCP server |
| **Friend Agent** | CrewAI | `10006` | Knows the friend's calendar, favorite genres and already-watched movies |
| **Host Agent** | Google ADK | ADK Web UI (`8000`) | Calls the other two over A2A, filters out watched movies and books the plan |

```text
 You ──▶ Host Agent (ADK, adk web)
            │  RemoteA2aAgent ──A2A──▶ Movie Agent (ADK, to_a2a) ──Cypher + MCP──▶ Neo4j
            │  RemoteA2aAgent ──A2A──▶ Friend Agent (CrewAI + a2a-sdk server)
            └─ confirm / list / cancel movie plans
```

## Repository layout

- `Problem/`: starter code with `# TODO` placeholders (used by the codelab). Placeholders are valid Python, so you can test each step as you go.
- `Solution/`: the finished, working code.
- `Notebook/`: Jupyter notebooks for exploring the Neo4j movie graph.

Each of `Problem/` and `Solution/` contains:

- `movie_agent/`: `agent.py` (Neo4j tools, Neo4j MCP toolset and ADK agent) and `__main__.py` (Agent Card + A2A server)
- `friend_agent/`: `agent.py` (CrewAI agent), `agent_executor.py` (A2A executor) and `__main__.py` (Agent Card + A2A server)
- `host_agent/host/`: `agent.py` (orchestrator) and `movie_tools.py` (plan tools)

## Prerequisites

- Python **3.11 – 3.13**
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- A Neo4j database with the *Recommendations* dataset. The public, read-only demo database below works out of the box.
- Internet access the first time the Movie Agent starts: `uvx` (from the `uv` package in `requirements.txt`) downloads the Neo4j MCP server `mcp-neo4j-cypher@0.6.0`.

## Setup

```bash
git clone https://github.com/KillerStrike17/A2A-Protocol-with-Neo4j.git
cd A2A-Protocol-with-Neo4j

python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```bash
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Neo4j public read-only demo database (Recommendations dataset)
NEO4J_URI=neo4j+s://demo.neo4jlabs.com
NEO4J_USERNAME=recommendations
NEO4J_PASSWORD=recommendations
NEO4J_DATABASE=recommendations

# Optional: public URL the Friend Agent advertises in its Agent Card
HOST_OVERRIDE=
```

`load_dotenv()` searches parent folders, so the agents find this file from any sub-folder.

## Run

Start each service in its own terminal (virtual environment activated). Use `Solution/` for the finished code, or `Problem/` after you have completed the TODOs.

```bash
# Terminal 1: Movie Agent  -> http://localhost:10005
cd Solution/movie_agent
python .

# Terminal 2: Friend Agent -> http://localhost:10006
cd Solution/friend_agent
python .

# Terminal 3: Host Agent in the ADK Web UI -> http://localhost:8000
cd Solution/host_agent
adk web
```

Open http://localhost:8000, select **host**, and try:

- `Recommend a movie I can watch with my friend.`
- `Check when my friend is free tomorrow and book your top pick at a time that works.`
- `Show me all my movie plans.`
- `Ask the movie agent: which 5 actors appear in the most Sci-Fi movies?` (answered through the Neo4j **MCP** server)

Each agent publishes its A2A Agent Card at `/.well-known/agent-card.json`, for example:

```bash
curl http://localhost:10005/.well-known/agent-card.json
```

## Configuration notes

- **Model:** all agents use `gemini-3.8-flash` (`MODEL` in `movie_agent/agent.py` and `host_agent/host/agent.py`, and `gemini/gemini-3.8-flash` in `friend_agent/agent.py`).
- **Ports:** if you change them, update the Agent Card URLs in `host_agent/host/agent.py`.
- **CrewAI tracing:** `friend_agent/agent.py` sets `CREWAI_TRACING_ENABLED=false` so CrewAI doesn't pause each request with an interactive prompt.

## Neo4j notes

- The Movie Agent shares one Neo4j driver (`get_neo4j_driver()`) and runs **parameterized** Cypher with `driver.execute_query(...)`, for example `MATCH (m:Movie)-[:IN_GENRE]->(g:Genre {name: $genre})`.
- **MCP:** `create_neo4j_mcp_toolset()` launches `mcp-neo4j-cypher@0.6.0` with `uvx` over stdio, in read-only mode, and exposes only `get_neo4j_schema` and `read_neo4j_cypher` to the agent.
- Useful `Movie` properties in the Recommendations dataset: `title`, `year`, `imdbRating`, `plot`, `released`. Relationships: `IN_GENRE`, `ACTED_IN`, `DIRECTED`.
- Browse the demo database at https://demo.neo4jlabs.com:7473/browser/ with the same credentials.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `404 NOT_FOUND ... model ... is no longer available` | Update the model name (see *Configuration notes*). |
| `429 RESOURCE_EXHAUSTED` | Your Gemini quota is used up. Wait for it to reset or enable billing in AI Studio. |
| `Neo4j connection error` | Check the four `NEO4J_*` values in `.env`. |
| Host says it can't reach an agent | Make sure the Movie and Friend agents are running on ports 10005 and 10006. |
| `...will run without the tools from toolset McpToolset` | `uvx` is missing or couldn't download the MCP server. Run `pip install uv` and check your internet connection. |
| `adk web` lists no **host** app | Run `adk web` from inside `host_agent/`, not from `Solution/`. |
| Port already in use | Stop the old process that's using port 10005, 10006 or 8000. |
