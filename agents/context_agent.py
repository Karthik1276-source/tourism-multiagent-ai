import os
import json
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Force-load .env from the project root, no matter where this script is run from
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(city: str) -> dict:
    """Fetch current weather for a city using OpenWeatherMap."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": OPENWEATHER_KEY, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "success": True,
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
        }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_seasonal_context(destination: str) -> dict:
    """Check if destination has a seasonal event happening around now."""
    data_path = Path(__file__).resolve().parent.parent / "data" / "seasonal_events.json"

    with open(data_path, "r") as f:
        events = json.load(f)

    current_month = datetime.now().month
    matches = []

    for event in events:
        if event["destination"].lower() == destination.lower():
            start, end = event["start_month"], event["end_month"]
            in_season = (
                start <= current_month <= end
                if start <= end
                else current_month >= start or current_month <= end
            )
            matches.append({**event, "in_season": in_season})

    return {"destination": destination, "events": matches}


def run_context_agent(destination: str, city_for_weather: str = None) -> dict:
    """Main entry point for the Context Agent."""
    weather = get_weather(city_for_weather or destination)
    seasonal = get_seasonal_context(destination)

    return {
        "destination": destination,
        "weather": weather,
        "seasonal_context": seasonal,
    }


# Quick standalone test
if __name__ == "__main__":
    result = run_context_agent("Ooty")
    print(json.dumps(result, indent=2))