import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.context_agent import run_context_agent
from agents.ranking_agent import run_ranking_agent
from agents.itinerary_agent import run_itinerary_agent
from agents.explanation_agent import run_explanation_agent
from agents.culture_language_agent import run_culture_language_agent


def run_pipeline(user_input: dict) -> dict:
    """
    user_input example:
    {
        "destination": "Ooty",
        "state": "Tamil Nadu",
        "candidate_places": [{"name": "...", "tags": [...]}],
        "preferences": {"interests": [...], "budget": "medium"},
        "num_days": 3,
        "home_language": "Tamil",
        "destination_language": "Tamil"
    }
    """
    context = run_context_agent(user_input["destination"])

    ranked = run_ranking_agent(
        user_input["candidate_places"], user_input["preferences"], context
    )

    itinerary = run_itinerary_agent(ranked, user_input["num_days"])

    explanations = {
        dest["name"]: run_explanation_agent(dest["name"], dest["score"], context)
        for dest in ranked
    }

    culture = run_culture_language_agent(
        user_input["state"], user_input["home_language"], user_input["destination_language"]
    )

    return {
        "context": context,
        "ranked_places": ranked,
        "itinerary": itinerary,
        "explanations": explanations,
        "culture_language": culture,
    }


if __name__ == "__main__":
    sample_input = {
        "destination": "Ooty",
        "state": "Tamil Nadu",
        "candidate_places": [
            {"name": "Ooty Botanical Garden", "tags": ["nature", "family"]},
            {"name": "Doddabetta Peak", "tags": ["nature", "adventure"]},
        ],
        "preferences": {"interests": ["nature", "family"], "budget": "medium"},
        "num_days": 2,
        "home_language": "Tamil",
        "destination_language": "Tamil",
    }
    import json
    print(json.dumps(run_pipeline(sample_input), indent=2))