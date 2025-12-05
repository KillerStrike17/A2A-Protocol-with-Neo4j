from datetime import date, datetime
from typing import Dict, List
from uuid import uuid4

# In-memory database for movie watching plans
MOVIE_PLANS: Dict[str, dict] = {}


def confirm_movie_plan(
    movie_title: str, date: str, time: str, participants: str = "Sushmita"
) -> dict:
    """
    Confirms and saves a movie watching plan.

    Args:
        movie_title: The title of the movie to watch.
        date: The date to watch the movie, in YYYY-MM-DD format.
        time: The time to watch the movie, in HH:MM format.
        participants: The participants for the movie watching (default: "Sushmita").

    Returns:
        A dictionary confirming the plan or providing an error.
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
        datetime.strptime(time, "%H:%M")
    except ValueError:
        return {
            "status": "error",
            "message": "Invalid date or time format. Please use YYYY-MM-DD and HH:MM.",
        }

    if not movie_title:
        return {
            "status": "error",
            "message": "Cannot confirm a plan without a movie title.",
        }

    plan_id = str(uuid4())
    plan = {
        "id": plan_id,
        "movie_title": movie_title,
        "date": date,
        "time": time,
        "participants": participants,
        "created_at": datetime.now().isoformat(),
    }

    MOVIE_PLANS[plan_id] = plan

    return {
        "status": "success",
        "message": f"Movie plan confirmed! Movie: {movie_title}, Date: {date}, Time: {time}, Participants: {participants}. Plan ID: {plan_id}",
        "plan_id": plan_id,
        "plan": plan,
    }


def get_movie_plans(date_filter: str = None) -> dict:
    """
    Retrieves movie watching plans, optionally filtered by date.

    Args:
        date_filter: Optional date filter in YYYY-MM-DD format. If provided, only returns plans for that date.

    Returns:
        A dictionary with the list of movie plans.
    """
    if date_filter:
        try:
            datetime.strptime(date_filter, "%Y-%m-%d")
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid date format. Please use YYYY-MM-DD.",
            }
        filtered_plans = [
            plan
            for plan in MOVIE_PLANS.values()
            if plan["date"] == date_filter
        ]
        return {
            "status": "success",
            "message": f"Found {len(filtered_plans)} movie plan(s) for {date_filter}.",
            "plans": filtered_plans,
        }

    all_plans = list(MOVIE_PLANS.values())
    # Sort by date and time
    all_plans.sort(key=lambda x: (x["date"], x["time"]))

    return {
        "status": "success",
        "message": f"Found {len(all_plans)} movie plan(s).",
        "plans": all_plans,
    }


def cancel_movie_plan(plan_id: str) -> dict:
    """
    Cancels a movie watching plan by plan ID.

    Args:
        plan_id: The ID of the plan to cancel.

    Returns:
        A dictionary confirming the cancellation or providing an error.
    """
    if not plan_id:
        return {
            "status": "error",
            "message": "Cannot cancel a plan without a plan ID.",
        }

    if plan_id not in MOVIE_PLANS:
        return {
            "status": "error",
            "message": f"Plan with ID {plan_id} not found.",
        }

    plan = MOVIE_PLANS.pop(plan_id)
    return {
        "status": "success",
        "message": f"Movie plan cancelled: {plan['movie_title']} on {plan['date']} at {plan['time']}.",
    }
