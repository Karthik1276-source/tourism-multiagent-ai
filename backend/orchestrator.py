import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.context_agent import run_context_agent
from agents.ranking_agent import run_ranking_agent
from agents.itinerary_agent import run_itinerary_agent
from agents.explanation_agent import run_explanation_agent, generate_trip_summary_explanation
from agents.culture_language_agent import run_culture_language_agent
from agents.travel_time_agent import run_travel_time_agent, geocode_place
from agents.budget_agent import run_budget_agent
from agents.poi_agent import run_poi_agent
from agents.map_agent import google_maps_directions_url, google_maps_search_url
from agents.amenities_agent import run_amenities_agent


def run_pipeline(user_input: dict) -> dict:
    """
    user_input example:
    {
        "destination": "Ooty",
        "state": "Tamil Nadu",
        "origin_place": "Ooty Bus Stand",
        "preferences": {"interests": [...], "budget": "medium"},
        "total_budget": 5000,
        "num_days": 3,
        "home_language": "Tamil",
        "destination_language": "Tamil"
    }
    """
    candidate_places = run_poi_agent(user_input["destination"])

    if not candidate_places:
        return {"error": f"No tourist places found near '{user_input['destination']}'. Try a nearby larger town/city name."}

    context = run_context_agent(user_input["destination"])

    ranked = run_ranking_agent(candidate_places, user_input["preferences"], context)

    with_travel_time = run_travel_time_agent(
        user_input.get("origin_place", user_input["destination"]), ranked
    )

    budget_result = run_budget_agent(
        with_travel_time, user_input["total_budget"], user_input["num_days"]
    )

    # Attach Google Maps navigation links to each affordable place
    origin_geo = geocode_place(user_input.get("origin_place", user_input["destination"]))

    for place in budget_result["affordable_places"]:
        if place.get("latitude") and place.get("longitude"):
            if origin_geo.get("success"):
                place["google_maps_url"] = google_maps_directions_url(
                    place["latitude"], place["longitude"],
                    origin_geo["latitude"], origin_geo["longitude"]
                )
            else:
                place["google_maps_url"] = google_maps_directions_url(place["latitude"], place["longitude"])
        else:
            place["google_maps_url"] = google_maps_search_url(place["name"], place["area"])

    # Time-aware itinerary (Morning/Afternoon/Evening grouped, per day)
    itinerary = run_itinerary_agent(budget_result["affordable_places"], user_input["num_days"])

    explanations = {
        dest["name"]: run_explanation_agent(dest["name"], dest.get("score", 0), context)
        for dest in budget_result["affordable_places"]
    }

    culture = run_culture_language_agent(
        user_input["state"], user_input["home_language"], user_input["destination_language"]
    )

    # Fetch nearby hotels, hospitals, and pharmacies around the destination area
    dest_geo = geocode_place(user_input["destination"])
    if dest_geo.get("success"):
        amenities = run_amenities_agent(dest_geo["latitude"], dest_geo["longitude"])
    else:
        amenities = {"success": False, "hotels": [], "hospitals": [], "pharmacies": []}

    # Rule-based "Why this itinerary?" summary
    trip_summary = generate_trip_summary_explanation(
        budget_result["affordable_places"], budget_result["breakdown"], user_input["num_days"]
    )

    return {
        "context": context,
        "all_places_with_travel_and_budget": budget_result["all_places"],
        "affordable_places": budget_result["affordable_places"],
        "total_estimated_cost": budget_result["total_estimated_cost"],
        "budget_remaining": budget_result["budget_remaining"],
        "budget_breakdown": budget_result["breakdown"],
        "itinerary": itinerary,
        "explanations": explanations,
        "culture_language": culture,
        "amenities": amenities,
        "trip_summary": trip_summary,
    }