import os
from typing import Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from neo4j import GraphDatabase
load_dotenv()
# Neo4j connection parameters from environment variables
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")
# global driver

print("NEO4j URI:",NEO4J_URI)
URI = NEO4J_URI
AUTH = (NEO4J_USER, NEO4J_PASSWORD)

def get_neo4j_driver():
    """Get a Neo4j driver instance."""
    driver = GraphDatabase.driver(URI, auth=AUTH)
    try:
        print("Checking connectivity")
        driver.verify_connectivity()
        print("Neo4j connection successful")
    except Exception as e:
        print(f"Neo4j connection error: {e}")
        driver.close()
        raise
    return driver


def recommend_movies_by_genre(genre: str, limit: int = 10) -> str:
    """
    Recommends movies based on a specific genre.

    Args:
        genre: The genre to search for (e.g., "Action", "Comedy", "Drama").
        limit: Maximum number of recommendations to return (default: 10).

    Returns:
        A string listing recommended movies with their details.
    """
    print("in genre Function")
    print("#"*100)
    driver = get_neo4j_driver()
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            query = """
            MATCH (m:Movie)-[:IN_GENRE]->(g:Genre {name: $genre})
            RETURN m.title AS title, m.released AS year, m.tagline AS tagline, m.rating AS rating
            ORDER BY m.rating DESC
            LIMIT $limit
            """
            print("Running query")
            print("#"*100)
            print(f"Query: {query}")
            print(f"Parameters: genre={genre}, limit={limit}")
            print("#"*100)
            result = session.run(query, genre=genre, limit=limit)
            
            print("Query Executed")
            print("#"*100)
            movies = []
            for record in result:
                title = record["title"] or "Unknown"
                year = record["year"] or "Unknown"
                tagline = record["tagline"] or ""
                rating = record["rating"] or "N/A"
                movie_info = f"- {title} ({year})"
                if tagline:
                    movie_info += f" - {tagline}"
                movie_info += f" [Rating: {rating}]"
                movies.append(movie_info)
            
            if movies:
                return f"Here are {len(movies)} {genre} movie recommendations:\n" + "\n".join(movies)
            else:
                return f"No movies found for genre: {genre}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"
    finally:
        driver.close()


def recommend_movies_by_actor(actor_name: str, limit: int = 10) -> str:
    """
    Recommends movies featuring a specific actor.

    Args:
        actor_name: The name of the actor.
        limit: Maximum number of recommendations to return (default: 10).

    Returns:
        A string listing movies featuring the actor.
    """
    driver = get_neo4j_driver()
    try:
        with driver.session(database=NEO4J_DATABASE) as neo4j_session:
            query = """
            MATCH (a:Person {name: $actor_name})-[:ACTED_IN]->(m:Movie)
            RETURN m.title AS title, m.released AS year, m.rating AS rating
            ORDER BY m.rating DESC
            LIMIT $limit
            """
            result = neo4j_session.run(query, actor_name=actor_name, limit=limit)
            movies = []
            for record in result:
                title = record["title"] or "Unknown"
                year = record["year"] or "Unknown"
                rating = record["rating"] or "N/A"
                movies.append(f"- {title} ({year}) [Rating: {rating}]")
            
            if movies:
                return f"Movies featuring {actor_name}:\n" + "\n".join(movies)
            else:
                return f"No movies found for actor: {actor_name}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"
    finally:
        driver.close()


def recommend_movies_by_director(director_name: str, limit: int = 10) -> str:
    """
    Recommends movies directed by a specific director.

    Args:
        director_name: The name of the director.
        limit: Maximum number of recommendations to return (default: 10).

    Returns:
        A string listing movies directed by the director.
    """
    driver = get_neo4j_driver()
    try:
        with driver.session(database=NEO4J_DATABASE) as neo4j_session:
            query = """
            MATCH (d:Person {name: $director_name})-[:DIRECTED]->(m:Movie)
            RETURN m.title AS title, m.released AS year, m.rating AS rating
            ORDER BY m.rating DESC
            LIMIT $limit
            """
            result = neo4j_session.run(query, director_name=director_name, limit=limit)
            movies = []
            for record in result:
                title = record["title"] or "Unknown"
                year = record["year"] or "Unknown"
                rating = record["rating"] or "N/A"
                movies.append(f"- {title} ({year}) [Rating: {rating}]")
            
            if movies:
                return f"Movies directed by {director_name}:\n" + "\n".join(movies)
            else:
                return f"No movies found for director: {director_name}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"
    finally:
        driver.close()


def recommend_movies_by_year(year: int, limit: int = 10) -> str:
    """
    Recommends movies released in a specific year.

    Args:
        year: The release year.
        limit: Maximum number of recommendations to return (default: 10).

    Returns:
        A string listing movies from that year.
    """
    driver = get_neo4j_driver()
    try:
        with driver.session(database=NEO4J_DATABASE) as neo4j_session:
            query = """
            MATCH (m:Movie)
            WHERE m.year = $year
            RETURN m.title AS title, m.tagline AS tagline, m.rating AS rating
            ORDER BY m.rating DESC
            LIMIT $limit
            """
            result = neo4j_session.run(query, year=year, limit=limit)
            movies = []
            for record in result:
                title = record["title"] or "Unknown"
                tagline = record["tagline"] or ""
                rating = record["rating"] or "N/A"
                movie_info = f"- {title}"
                if tagline:
                    movie_info += f" - {tagline}"
                movie_info += f" [Rating: {rating}]"
                movies.append(movie_info)
            
            if movies:
                return f"Top movies from {year}:\n" + "\n".join(movies)
            else:
                return f"No movies found for year: {year}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"
    finally:
        driver.close()


def search_movies_by_keyword(keyword: str, limit: int = 10) -> str:
    """
    Searches for movies by title or tagline keyword.

    Args:
        keyword: The keyword to search for in movie titles or taglines.
        limit: Maximum number of results to return (default: 10).

    Returns:
        A string listing matching movies.
    """
    driver = get_neo4j_driver()
    try:
        with driver.session(database=NEO4J_DATABASE) as neo4j_session:
            query = """
            MATCH (m:Movie)
            WHERE toLower(m.title) CONTAINS toLower($keyword) 
               OR toLower(m.tagline) CONTAINS toLower($keyword)
            RETURN m.title AS title, m.released AS year, m.tagline AS tagline, m.rating AS rating
            ORDER BY m.rating DESC
            LIMIT $limit
            """
            result = neo4j_session.run(query, keyword=keyword, limit=limit)
            movies = []
            for record in result:
                title = record["title"] or "Unknown"
                year = record["year"] or "Unknown"
                tagline = record["tagline"] or ""
                rating = record["rating"] or "N/A"
                movie_info = f"- {title} ({year})"
                if tagline:
                    movie_info += f" - {tagline}"
                movie_info += f" [Rating: {rating}]"
                movies.append(movie_info)
            
            if movies:
                return f"Movies matching '{keyword}':\n" + "\n".join(movies)
            else:
                return f"No movies found matching: {keyword}"
    except Exception as e:
        return f"Error querying movies: {str(e)}"
    finally:
        driver.close()


def get_movie_details(movie_title: str) -> str:
    """
    Gets detailed information about a specific movie.

    Args:
        movie_title: The title of the movie.

    Returns:
        A string with detailed movie information.
    """
    driver = get_neo4j_driver()
    try:
        with driver.session(database=NEO4J_DATABASE) as neo4j_session:
            query = """
            MATCH (m:Movie {title: $movie_title})
            OPTIONAL MATCH (m)-[:IN_GENRE]->(g:Genre)
            OPTIONAL MATCH (m)<-[:ACTED_IN]-(a:Person)
            OPTIONAL MATCH (m)<-[:DIRECTED]-(d:Person)
            RETURN m.title AS title, 
                   m.released AS year, 
                   m.tagline AS tagline, 
                   m.rating AS rating,
                   collect(DISTINCT g.name) AS genres,
                   collect(DISTINCT a.name) AS actors,
                   collect(DISTINCT d.name) AS directors
            """
            result = neo4j_session.run(query, movie_title=movie_title)
            record = result.single()
            
            if not record:
                return f"Movie not found: {movie_title}"
            
            details = [f"Title: {record['title'] or 'Unknown'}"]
            if record['year']:
                details.append(f"Year: {record['year']}")
            if record['tagline']:
                details.append(f"Tagline: {record['tagline']}")
            if record['rating']:
                details.append(f"Rating: {record['rating']}")
            if record['genres']:
                details.append(f"Genres: {', '.join(record['genres'])}")
            if record['directors']:
                details.append(f"Directors: {', '.join(record['directors'])}")
            if record['actors']:
                details.append(f"Actors: {', '.join(record['actors'][:10])}")  # Limit to first 10
            
            return "\n".join(details)
    except Exception as e:
        return f"Error querying movie details: {str(e)}"
    # finally:
    #     driver.close()


def create_agent() -> LlmAgent:
    """Constructs the ADK agent for movie recommendations."""

    # driver = get_neo4j_driver()

    return LlmAgent(
        model="gemini-2.0-flash",
        name="Movie_Agent",
        instruction="""
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
                    or tagline keywords.
            *   **Movie Details:** Use `get_movie_details` to get comprehensive information about 
                    a specific movie.
            *   **Be Helpful and Conversational:** Engage naturally with users, ask clarifying 
                    questions if needed, and provide thoughtful recommendations.
            *   **Combine Criteria:** If users provide multiple criteria (e.g., genre and year), 
                    use multiple tools to provide comprehensive recommendations.
        """,
        tools=[
            recommend_movies_by_genre,
            recommend_movies_by_actor,
            recommend_movies_by_director,
            recommend_movies_by_year,
            search_movies_by_keyword,
            get_movie_details,
        ],
    )
