import os
import random
from datetime import date, datetime, timedelta
from typing import Type

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


def generate_calendar() -> dict[str, list[str]]:
    """Generates a random calendar for the next 7 days."""
    calendar = {}
    today = date.today()
    possible_times = [f"{h:02}:00" for h in range(8, 21)]  # 8 AM to 8 PM

    for i in range(7):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        available_slots = sorted(random.sample(possible_times, 8))
        calendar[date_str] = available_slots
    print("---- Sushmita's Generated Calendar ----")
    print(calendar)
    print("---------------------------------")
    return calendar


MY_CALENDAR = generate_calendar()

# Movie preferences and watched movies list
MOVIE_GENRE_PREFERENCES = [
    "Action",
    "Comedy",
    "Drama",
    "Sci-Fi",
    "Thriller",
    "Romance",
]

WATCHED_MOVIES = [
    "The Matrix",
    "Inception",
    "Interstellar",
    "The Dark Knight",
    "Pulp Fiction",
    "Forrest Gump",
    "The Shawshank Redemption",
    "Titanic",
    "Avatar",
    "The Avengers",
]


class AvailabilityToolInput(BaseModel):
    """Input schema for AvailabilityTool."""

    date_range: str = Field(
        ...,
        description="The date or date range to check for availability, e.g., '2024-07-28' or '2024-07-28 to 2024-07-30'.",
    )


class AvailabilityTool(BaseTool):
    name: str = "Calendar Availability Checker"
    description: str = (
        "Checks my availability for a given date or date range. "
        "Use this to find out when I am free."
    )
    args_schema: Type[BaseModel] = AvailabilityToolInput

    def _run(self, date_range: str) -> str:
        """Checks my availability for a given date range."""
        dates_to_check = [d.strip() for d in date_range.split("to")]
        start_date_str = dates_to_check[0]
        end_date_str = dates_to_check[-1]

        try:
            start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            if start > end:
                return (
                    "Invalid date range. The start date cannot be after the end date."
                )

            results = []
            delta = end - start
            for i in range(delta.days + 1):
                day = start + timedelta(days=i)
                date_str = day.strftime("%Y-%m-%d")
                available_slots = MY_CALENDAR.get(date_str, [])
                if available_slots:
                    availability = f"On {date_str}, I am available at: {', '.join(available_slots)}."
                    results.append(availability)
                else:
                    results.append(f"I am not available on {date_str}.")

            return "\n".join(results)

        except ValueError:
            return (
                "I couldn't understand the date. "
                "Please ask to check availability for a date like 'YYYY-MM-DD'."
            )


class MoviePreferencesToolInput(BaseModel):
    """Input schema for MoviePreferencesTool."""

    query: str = Field(
        ...,
        description="The query about movie preferences - can ask about favorite genres or watched movies.",
    )


class MoviePreferencesTool(BaseTool):
    name: str = "Movie Preferences Manager"
    description: str = (
        "Gets my movie genre preferences and list of movies I've already watched. "
        "Use this to find out what genres of movies I like and which movies I've seen."
    )
    args_schema: Type[BaseModel] = MoviePreferencesToolInput

    def _run(self, query: str) -> str:
        """Returns movie genre preferences and watched movies list."""
        query_lower = query.lower()
        
        if "genre" in query_lower or "preference" in query_lower or "like" in query_lower:
            genres_str = ", ".join(MOVIE_GENRE_PREFERENCES)
            return (
                f"My favorite movie genres are: {genres_str}. "
                f"I enjoy watching movies in these genres."
            )
        elif "watched" in query_lower or "seen" in query_lower or "already" in query_lower:
            movies_str = ", ".join(WATCHED_MOVIES)
            return (
                f"Here are the movies I've already watched: {movies_str}. "
                f"Please don't recommend these movies as I've already seen them."
            )
        else:
            # Return both if query is general
            genres_str = ", ".join(MOVIE_GENRE_PREFERENCES)
            movies_str = ", ".join(WATCHED_MOVIES)
            return (
                f"My favorite movie genres are: {genres_str}. "
                f"Movies I've already watched: {movies_str}."
            )


class SchedulingAgent:
    """Agent that handles scheduling tasks."""

    SUPPORTED_CONTENT_TYPES = ["text/plain"]

    def __init__(self):
        """Initializes the SchedulingAgent."""
        if os.getenv("GOOGLE_API_KEY"):
            self.llm = LLM(
                model=# TODO,
                api_key=# TODO,
            )
        else:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        self.scheduling_assistant = Agent(
            role=# TODO,
            goal=(
                # TODO
            ),
            backstory=(
               # TODO
            ),
            verbose=True,
            allow_delegation=False,
            tools=# TODO,
            llm=# TODO,
        )

    def invoke(self, question: str) -> str:
        """Kicks off the crew to answer questions about availability or movie preferences."""
        task_description = (
            # TODO
        )

        check_availability_task = Task(
            description=task_description,
            expected_output=(
               # TODO
            ),
            agent=self.scheduling_assistant,
        )

        crew = Crew(
            agents=# TODO,
            tasks= # TODO,
            process=# TODO,
            verbose=True,
        )
        result = crew.kickoff()
        return str(result)
