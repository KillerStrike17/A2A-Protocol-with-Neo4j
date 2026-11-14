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

## Test it locally

Work through these checks in order. Each layer builds on the previous one, so if a check fails, fix it before moving on. Run them from the repository root with the virtual environment activated, unless a step says otherwise.

### 1. Installation

```bash
python --version   # must be 3.11, 3.12 or 3.13
python -c "import google.adk, a2a, crewai, neo4j; print('All imports OK')"
uvx --version      # needed for the Neo4j MCP server
```

### 2. Neo4j connection and the Cypher tools (no LLM calls)

```bash
cd Solution/movie_agent
python -c "from agent import get_neo4j_driver; get_neo4j_driver().close(); print('Connected to Neo4j!')"
python -c "from agent import recommend_movies_by_genre; print(recommend_movies_by_genre('Comedy', 5))"
python -c "from agent import create_agent; a = create_agent(); print(a.name, a.model, len(a.tools), 'tools')"
cd ../..
```

Expected output:

```text
Connected to Neo4j!
Top 5 Comedy movies:
- Bill Hicks: Revelations (1993) [IMDb: 8.9]
- George Carlin: Jammin' in New York (1992) [IMDb: 8.9]
- Pulp Fiction (1994) [IMDb: 8.9]
- Bill Hicks: Relentless (1992) [IMDb: 8.8]
- Fawlty Towers (1975 (Unknown) [IMDb: 8.8]
Movie_Agent gemini-3.8-flash 7 tools
```

The 7 tools are the six Cypher tools plus the Neo4j MCP toolset.

### 3. Start the agents

Start the Movie Agent (Terminal 1) and the Friend Agent (Terminal 2) as described in [Run](#run). On its first start, the Movie Agent downloads the MCP server with `uvx`, which takes about 30 seconds.

Check that both Agent Cards are served:

```bash
curl http://localhost:10005/.well-known/agent-card.json   # "name": "Movie Agent"
curl http://localhost:10006/.well-known/agent-card.json   # "name": "Friend Agent", two skills
```

### 4. Call each agent directly over A2A

This sends a raw A2A `SendMessage` JSON-RPC request, the same kind of request the Host Agent sends.

macOS / Linux (bash):

```bash
curl -s http://localhost:10006/ \
  -H "Content-Type: application/json" -H "A2A-Version: 1.0" \
  -d '{"jsonrpc":"2.0","id":"1","method":"SendMessage","params":{"message":{"messageId":"m1","role":"ROLE_USER","parts":[{"text":"What genres of movies do you like?"}]}}}'
```

Windows (PowerShell):

```powershell
$body = '{"jsonrpc":"2.0","id":"1","method":"SendMessage","params":{"message":{"messageId":"m1","role":"ROLE_USER","parts":[{"text":"What genres of movies do you like?"}]}}}'
$r = Invoke-RestMethod -Uri http://localhost:10006/ -Method Post -ContentType "application/json" -Headers @{ "A2A-Version" = "1.0" } -Body $body
$r.result.task.status.state; $r.result.task.artifacts[0].parts[0].text
```

Expected: the task state is `TASK_STATE_COMPLETED`, and the artifact text lists the friend's genres (Action, Comedy, Drama, Sci-Fi, Thriller, Romance).

To test the Movie Agent, send the same request to `http://localhost:10005/` with the text `Recommend 3 top-rated Comedy movies`. To test MCP, use `Which 5 actors appear in the most Sci-Fi movies?`. Terminal 1 shows the MCP server starting, and the answer names Arnold Schwarzenegger and Will Smith (9 Sci-Fi movies each).

Each request uses the Gemini API, so expect a few seconds per answer.

### 5. Test the whole system in the ADK Web UI

Start Terminal 3 (`cd Solution/host_agent` then `adk web`), open http://127.0.0.1:8000, select **host**, and send these prompts in order:

| Prompt | What should happen |
|---|---|
| `Recommend a movie I can watch with my friend.` | The host calls `Friend_Agent` and then `Movie_Agent`. None of the recommendations are on the friend's watched list (The Matrix, Inception, Interstellar, The Dark Knight, Pulp Fiction, Forrest Gump, The Shawshank Redemption, Titanic, Avatar, The Avengers). |
| `Check when my friend is free tomorrow and book your top pick at a time that works.` | `Friend_Agent` returns tomorrow's free slots, then `confirm_movie_plan` books one of them and returns a **Plan ID**. |
| `Show me all my movie plans.` | `get_movie_plans` lists the plan. |
| `Cancel that plan.` | `cancel_movie_plan` confirms the cancellation. |
| `Ask the movie agent: which 5 actors appear in the most Sci-Fi movies?` | The Movie Agent uses the MCP tools `get_neo4j_schema` and `read_neo4j_cypher`. |

Use the **Events** panel on the left to inspect each tool call and the A2A request and response.

### 6. Test your own work in `Problem/`

After finishing the TODOs in `Problem/`, run the same checks with `Problem/` in place of `Solution/`. Because every TODO placeholder is valid Python, you can run the step 2 checks as soon as you finish the matching codelab step.

### Stopping everything

Press `Ctrl+C` in each terminal. If a port is still busy afterwards, find the process that's using it:

```bash
# macOS / Linux
lsof -i :10005
# Windows (PowerShell)
Get-NetTCPConnection -LocalPort 10005 -State Listen | Select-Object OwningProcess
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
