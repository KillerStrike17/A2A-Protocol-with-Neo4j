import os
import shutil
import sys

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from neo4j import GraphDatabase

load_dotenv()

# Neo4j connection parameters from environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

URI = NEO4J_URI
AUTH = (NEO4J_USER, NEO4J_PASSWORD)

MODEL = "gemini-3.8-flash"

# `uvx` (installed with the `uv` package) launches the Neo4j MCP server. Look for it
# next to the running Python first, so it is found even if the venv isn't activated.
UVX = shutil.which("uvx", path=os.pathsep.join([os.path.dirname(sys.executable), os.environ.get("PATH", "")])) or "uvx"


_driver = None


def get_neo4j_driver():
    """Returns the shared Neo4j driver, creating it on first use.

    A driver is thread-safe and expensive to create, so the app keeps one
    instance and reuses it for every query.
    """
    global _driver
    if _driver is None:
        # TODO (Step 4): create a driver with GraphDatabase.driver(...)
        driver = None
        try:
            # TODO (Step 4): check that the database is reachable
            pass
        except Exception as e:
            print(f"Neo4j connection error: {e}")
            # TODO (Step 4): close the driver before re-raising the error
            raise
        _driver = driver
    return _driver


def _format_movie(record) -> str:
    """Formats one movie record as a single line of text."""
    title = record["title"] or "Unknown"
    year = record["year"] or "Unknown"
    rating = record["rating"] if record["rating"] is not None else "N/A"
    return f"- {title} ({year}) [IMDb: {rating}]"


def recommend_movies_by_genre(genre: str, limit: int) -> str:
    """
    Recommends the highest-rated movies in a specific genre.

    Args:
        genre: The genre to search for, e.g. "Action", "Comedy", "Drama", "Sci-Fi".
        limit: Maximum number of recommendations to return (use 10 if unsure).

    Returns:
        A string listing recommended movies with their year and IMDb rating.
    """
    try:
        # TODO (Step 5): write a parameterized Cypher query that returns the top-rated
        # movies in $genre as `title`, `year` and `rating`, limited to $limit.
        query = """ """
        # TODO (Step 5): run the query with get_neo4j_driver().execute_query(...)
        records = []
        movies = [_format_movie(record) for record in records]

        if movies:
            return f"Top {len(movies)} {genre} movies:\n" + "\n".join(movies)
        return f"No movies found for genre: {genre}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"


def recommend_movies_by_actor(actor_name: str, limit: int) -> str:
    """
    Recommends the highest-rated movies featuring a specific actor.

    Args:
        actor_name: The full name of the actor, e.g. "Tom Hanks".
        limit: Maximum number of recommendations to return (use 10 if unsure).

    Returns:
        A string listing movies featuring the actor.
    """
    try:
        query = """
        MATCH (a:Person {name: $actor_name})-[:ACTED_IN]->(m:Movie)
        RETURN m.title AS title, m.year AS year, m.imdbRating AS rating
        ORDER BY m.imdbRating DESC, m.title
        LIMIT $limit
        """
        records, _, _ = get_neo4j_driver().execute_query(
            query, actor_name=actor_name, limit=limit, database_=NEO4J_DATABASE
        )
        movies = [_format_movie(record) for record in records]

        if movies:
            return f"Movies featuring {actor_name}:\n" + "\n".join(movies)
        return f"No movies found for actor: {actor_name}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"


def recommend_movies_by_director(director_name: str, limit: int) -> str:
    """
    Recommends the highest-rated movies directed by a specific director.

    Args:
        director_name: The full name of the director, e.g. "Christopher Nolan".
        limit: Maximum number of recommendations to return (use 10 if unsure).

    Returns:
        A string listing movies directed by the director.
    """
    try:
        query = """
        MATCH (d:Person {name: $director_name})-[:DIRECTED]->(m:Movie)
        RETURN m.title AS title, m.year AS year, m.imdbRating AS rating
        ORDER BY m.imdbRating DESC, m.title
        LIMIT $limit
        """
        records, _, _ = get_neo4j_driver().execute_query(
            query, director_name=director_name, limit=limit, database_=NEO4J_DATABASE
        )
        movies = [_format_movie(record) for record in records]

        if movies:
            return f"Movies directed by {director_name}:\n" + "\n".join(movies)
        return f"No movies found for director: {director_name}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"


def recommend_movies_by_year(year: int, limit: int) -> str:
    """
    Recommends the highest-rated movies released in a specific year.

    Args:
        year: The release year, e.g. 1999.
        limit: Maximum number of recommendations to return (use 10 if unsure).

    Returns:
        A string listing movies from that year.
    """
    try:
        query = """
        MATCH (m:Movie)
        WHERE m.year = $year AND m.imdbRating IS NOT NULL
        RETURN m.title AS title, m.year AS year, m.imdbRating AS rating
        ORDER BY m.imdbRating DESC, m.title
        LIMIT $limit
        """
        records, _, _ = get_neo4j_driver().execute_query(
            query, year=year, limit=limit, database_=NEO4J_DATABASE
        )
        movies = [_format_movie(record) for record in records]

        if movies:
            return f"Top movies from {year}:\n" + "\n".join(movies)
        return f"No movies found for year: {year}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"


def search_movies_by_keyword(keyword: str, limit: int) -> str:
    """
    Searches for movies whose title or plot contains a keyword.

    Args:
        keyword: The keyword to search for, e.g. "space" or "heist".
        limit: Maximum number of results to return (use 10 if unsure).

    Returns:
        A string listing matching movies.
    """
    try:
        query = """
        MATCH (m:Movie)
        WHERE toLower(m.title) CONTAINS toLower($keyword)
           OR toLower(coalesce(m.plot, '')) CONTAINS toLower($keyword)
        RETURN m.title AS title, m.year AS year, m.imdbRating AS rating
        ORDER BY m.imdbRating DESC, m.title
        LIMIT $limit
        """
        records, _, _ = get_neo4j_driver().execute_query(
            query, keyword=keyword, limit=limit, database_=NEO4J_DATABASE
        )
        movies = [_format_movie(record) for record in records]

        if movies:
            return f"Movies matching '{keyword}':\n" + "\n".join(movies)
        return f"No movies found matching: {keyword}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"


def get_movie_details(movie_title: str) -> str:
    """
    Gets detailed information about a specific movie.

    Args:
        movie_title: The exact title of the movie.

    Returns:
        A string with the movie's year, rating, plot, genres, directors and actors.
    """
    try:
        query = """
        MATCH (m:Movie {title: $movie_title})
        OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
        OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
        OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
        RETURN m.title AS title,
               m.year AS year,
               m.plot AS plot,
               m.imdbRating AS rating,
               collect(DISTINCT g.name) AS genres,
               collect(DISTINCT a.name) AS actors,
               collect(DISTINCT d.name) AS directors
        LIMIT 1
        """
        records, _, _ = get_neo4j_driver().execute_query(
            query, movie_title=movie_title, database_=NEO4J_DATABASE
        )
        record = records[0] if records else None

        if not record:
            return f"Movie not found: {movie_title}"

        details = [f"Title: {record['title'] or 'Unknown'}"]
        if record["year"]:
            details.append(f"Year: {record['year']}")
        if record["rating"] is not None:
            details.append(f"IMDb rating: {record['rating']}")
        if record["plot"]:
            details.append(f"Plot: {record['plot']}")
        if record["genres"]:
            details.append(f"Genres: {', '.join(record['genres'])}")
        if record["directors"]:
            details.append(f"Directors: {', '.join(record['directors'])}")
        if record["actors"]:
            details.append(f"Actors: {', '.join(record['actors'][:10])}")

        return "\n".join(details)
    except Exception as e:
        return f"Error querying movie details: {str(e)}"


def create_neo4j_mcp_toolset() -> McpToolset:
    """Connects to the official Neo4j Cypher MCP server (read-only tools only).

    `uvx` downloads and runs the pinned server in a subprocess. ADK talks to it
    over stdio and turns its MCP tools into agent tools.
    """
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="",  # TODO (Step 7): the program that launches the server
                args=[],  # TODO (Step 7): the pinned server package and its transport
                env={
                    "NEO4J_URI": NEO4J_URI,
                    "NEO4J_USERNAME": NEO4J_USER,
                    "NEO4J_PASSWORD": NEO4J_PASSWORD,
                    "NEO4J_DATABASE": NEO4J_DATABASE,
                    "NEO4J_READ_ONLY": "true",  # the server hides write_neo4j_cypher
                    "NEO4J_SCHEMA_SAMPLE_SIZE": "1000",  # required by mcp-neo4j-cypher 0.6.0
                },
            ),
            timeout=60,  # the first run downloads the server, so allow extra time
        ),
        # Only expose the two read tools to the agent.
        tool_filter=[],  # TODO (Step 7): expose only the two read tools
    )


MOVIE_AGENT_INSTRUCTION = """
**Role:** You are a movie recommendation assistant that helps users discover movies
from a Neo4j database. Your goal is to provide personalized movie recommendations
based on user preferences.

**Core Directives:**

*   **Genre Recommendations:** Use `recommend_movies_by_genre` to find movies in a
        specific genre (e.g., Action, Comedy, Drama, Sci-Fi, Horror).
*   **Actor-based Recommendations:** Use `recommend_movies_by_actor` to find movies
        featuring a specific actor.
*   **Director-based Recommendations:** Use `recommend_movies_by_director` to find
        movies directed by a specific director.
*   **Year-based Recommendations:** Use `recommend_movies_by_year` to find movies
        from a specific release year.
*   **Keyword Search:** Use `search_movies_by_keyword` to search for movies by title
        or plot keywords.
*   **Movie Details:** Use `get_movie_details` to get comprehensive information about
        a specific movie.
*   **Be Helpful and Conversational:** Engage naturally with users, ask clarifying
        questions if needed, and provide thoughtful recommendations.
*   **Combine Criteria:** If users provide multiple criteria (e.g., genre and year),
        use multiple tools to provide comprehensive recommendations.
*   **Limits:** When the user does not say how many movies they want, use a limit of 10.
*   **Graph Questions (MCP):** For questions the tools above cannot answer (counts,
        rankings, e.g. "which actors appear in the most Sci-Fi movies?"), call
        `get_neo4j_schema` first, then answer with a read-only Cypher query via
        `read_neo4j_cypher`.
"""


def create_agent() -> LlmAgent:
    """Constructs the ADK agent for movie recommendations."""
    # TODO (Step 6): fill in the model, name, instruction and the six tools above.
    # TODO (Step 7): then add create_neo4j_mcp_toolset() to the tools list.
    return LlmAgent(
        model="",  # TODO
        name="",  # TODO
        description="Recommends movies from a Neo4j movie graph.",
        instruction="",  # TODO
        tools=[],  # TODO
    )
