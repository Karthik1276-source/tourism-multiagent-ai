import os
import requests
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ORS_API_KEY = os.getenv("ORS_API_KEY")


def geocode_place(place_name: str) -> dict:
    """Convert a place name into latitude/longitude using OpenStreetMap Nominatim (free, no key needed)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": place_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "tourism-multiagent-ai-fyp"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()
        if not results:
            return {"success": False, "error": "Place not found"}
        return {
            "success": True,
            "latitude": float(results[0]["lat"]),
            "longitude": float(results[0]["lon"]),
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_travel_time(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> dict:
    """Get driving distance & duration between two points using OpenRouteService."""
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ORS_API_KEY}
    params = {
        "start": f"{origin_lon},{origin_lat}",
        "end": f"{dest_lon},{dest_lat}",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        summary = data["features"][0]["properties"]["summary"]
        return {
            "success": True,
            "distance_km": round(summary["distance"] / 1000, 1),
            "duration_minutes": round(summary["duration"] / 60),
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_route_geometry(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> dict:
    """Get the actual route path (list of coordinates) for drawing on a map, using OpenRouteService."""
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {
        "coordinates": [[origin_lon, origin_lat], [dest_lon, dest_lat]]
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        coords = data["features"][0]["geometry"]["coordinates"]
        route_points = [[lat, lon] for lon, lat in coords]
        return {"success": True, "route_points": route_points}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def run_travel_time_agent(origin_place: str, destinations: list) -> list:
    """
    Given an origin place name and a list of POIs (each with latitude/longitude),
    return each POI annotated with distance_km and duration_minutes from the origin.
    """
    origin = geocode_place(origin_place)

    results = []
    for poi in destinations:
        if not origin.get("success"):
            results.append({**poi, "travel": {"success": False, "error": "Could not locate origin"}})
            continue

        if poi.get("latitude") is None or poi.get("longitude") is None:
            results.append({**poi, "travel": {"success": False, "error": "Destination coordinates missing"}})
            continue

        travel = get_travel_time(
            origin["latitude"], origin["longitude"],
            poi["latitude"], poi["longitude"]
        )
        results.append({**poi, "travel": travel})

    return results


if __name__ == "__main__":
    sample_pois = [
        {"name": "Ooty Botanical Garden", "latitude": 11.4128, "longitude": 76.7132},
        {"name": "Doddabetta Peak", "latitude": 11.4064, "longitude": 76.7333},
    ]
    import json
    print(json.dumps(run_travel_time_agent("Ooty Bus Stand", sample_pois), indent=2))