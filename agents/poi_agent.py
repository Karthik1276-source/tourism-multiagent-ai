import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from pathlib import Path
from agents.travel_time_agent import geocode_place

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "kaggle_raw" / "Top Indian Places to Visit.csv"

# Load once at import time — small dataset, no need to reload per request
_df = pd.read_csv(CSV_PATH)
_df.columns = [c.strip() for c in _df.columns]  # clean any stray whitespace in headers


def _row_to_poi(row: dict) -> dict:
    """Convert one dataset row into the POI dict shape the rest of the pipeline expects."""

    def clean_str(value, default="N/A"):
        """Handle NaN (empty cells) safely — pandas gives NaN, not None, for empty strings."""
        if pd.isna(value):
            return default
        return str(value)

    return {
        "name": clean_str(row["Name"]),
        "area": clean_str(row["City"]),
        "state": clean_str(row["State"]),
        "zone": clean_str(row["Zone"]),
        "tags": [clean_str(row["Type"]).lower(), clean_str(row["Significance"]).lower()],
        "entry_fee": float(row["Entrance Fee in INR"]) if pd.notna(row["Entrance Fee in INR"]) else 0,
        "avg_visit_hours": float(row["time needed to visit in hrs"]) if pd.notna(row["time needed to visit in hrs"]) else 1.5,
        "rating": float(row["Google review rating"]) if pd.notna(row["Google review rating"]) else None,
        "best_time_to_visit": clean_str(row.get("Best Time to visit"), "All"),
        "weekly_off": clean_str(row.get("Weekly Off"), "None"),
    }


def get_pois_by_city(city_name: str) -> list:
    """Return all POIs for a given city name from the dataset (case-insensitive match)."""
    matches = _df[_df["City"].str.lower() == city_name.lower()]
    return [_row_to_poi(row) for _, row in matches.iterrows()]


def attach_coordinates(pois: list) -> list:
    """
    The dataset has no lat/long, so geocode once per unique city
    (not per place) to keep this fast and avoid hammering the free geocoding API.
    """
    city_coords_cache = {}
    result = []

    for poi in pois:
        city = poi["area"]
        if city not in city_coords_cache:
            city_coords_cache[city] = geocode_place(city)

        coords = city_coords_cache[city]
        if coords.get("success"):
            poi["latitude"] = coords["latitude"]
            poi["longitude"] = coords["longitude"]
        else:
            poi["latitude"] = None
            poi["longitude"] = None

        result.append(poi)

    return result


def run_poi_agent(area_name: str) -> list:
    pois = get_pois_by_city(area_name)
    if not pois:
        return []
    return attach_coordinates(pois)


if __name__ == "__main__":
    import json
    print(json.dumps(run_poi_agent("Ooty"), indent=2))