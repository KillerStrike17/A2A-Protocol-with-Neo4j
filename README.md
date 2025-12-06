# A2A Protocol with Neo4j

This repo hosts three collaborating agents built on the A2A protocol and Google ADK:
- **Movie Agent** — answers movie recommendation queries backed by Neo4j.
- **Sushmita Agent** — shares availability, favorite genres, and already‑watched movies.
- **Host Agent** — coordinates between the two agents to propose a movie plan (asks availability only when requested), then can confirm/cancel plans.

## Prerequisites
- Python 3.10+
- Neo4j database accessible from your machine
- API access for Gemini (via `GOOGLE_API_KEY`) or Vertex (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`)

## Environment
Create a `.env` (at repo root) with:
```
GOOGLE_API_KEY=your_api_key              # required if not using Vertex
GOOGLE_GENAI_USE_VERTEXAI=FALSE          # set TRUE to skip API key check
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j                     # or your database name
HOST_OVERRIDE=                           # optional override for Sushmita Agent card URL
```

## Install
```
pip install -r requirements.txt
```

## Run the agents
Start each agent in its own terminal:
```
# Movie Agent (port 10005)
uv run --active .

# Sushmita Agent (port 10006)
uv run --active .
```
The Host Agent is a coordinating runner (no HTTP server here) and targets the above agents at:
```
http://localhost:10005  # Movie Agent
http://localhost:10006  # Sushmita Agent
```

uv run --active adk web

If you change ports, update `friend_agent_urls` in `host_agent/host/agent.py`.

## Neo4j usage notes
- The Movie Agent opens a Neo4j driver per request and closes it reliably.
- Queries are parameterized (e.g., `MATCH (m:Movie)-[:IN_GENRE]->(g:Genre {name: $genre})`).
- Ensure the Movie graph (Movie, Genre, Person, ACTED_IN, DIRECTED, IN_GENRE) exists in your database.

## Troubleshooting
- **Driver closed**: confirm `NEO4J_URI/USERNAME/PASSWORD/DATABASE` are correct and Neo4j is reachable.
- **Task not found between agents**: Host Agent now generates fresh task/context IDs per message; ensure agents are running on the configured ports.
- **Missing API key**: set `GOOGLE_API_KEY` or `GOOGLE_GENAI_USE_VERTEXAI=TRUE`.

## Key entry points
- `movie_agent/__main__.py` — starts Movie Agent (port 10005)
- `sushmita_agent/__main__.py` — starts Sushmita Agent (port 10006)
- `host_agent/host/agent.py` — Host Agent runner coordinating both agents
