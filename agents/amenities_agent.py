import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "tourism-multiagent-ai-fyp",
    "Accept": "application/json",
}


def fetch_nearby_amenities(lat: float, lon: float, radius_km: float = 5, limit: int = 8, retries: int = 2) -> dict:
    """
    Fetch nearby hotels, hospitals, and pharmacies from live OpenStreetMap data
    around a given coordinate. Retries once on timeout since Overpass is a shared free service.
    """
    radius_m = int(radius_km * 1000)

    query = f"""
    [out:json][timeout:40];
    (
      node["tourism"="hotel"](around:{radius_m},{lat},{lon});
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["amenity"="pharmacy"](around:{radius_m},{lat},{lon});
    );
    out body {limit * 3};
    """

    last_error = None
    data = None

    for attempt in range(retries + 1):
        try:
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                headers=HEADERS,
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            data = None

    if data is None:
        return {"success": False, "error": last_error, "hotels": [], "hospitals": [], "pharmacies": []}

    hotels, hospitals, pharmacies = [], [], []

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name")
        if not name:
            continue

        entry = {
            "name": name,
            "latitude": element["lat"],
            "longitude": element["lon"],
            "address": tags.get("addr:street", ""),
            "phone": tags.get("phone", tags.get("contact:phone", "N/A")),
        }

        if tags.get("tourism") == "hotel":
            entry["stars"] = tags.get("stars", "N/A")
            hotels.append(entry)
        elif tags.get("amenity") == "hospital":
            hospitals.append(entry)
        elif tags.get("amenity") == "pharmacy":
            pharmacies.append(entry)

    return {
        "success": True,
        "hotels": hotels[:limit],
        "hospitals": hospitals[:limit],
        "pharmacies": pharmacies[:limit],
    }


def run_amenities_agent(lat: float, lon: float) -> dict:
    return fetch_nearby_amenities(lat, lon)


if __name__ == "__main__":
    import json
    print(json.dumps(run_amenities_agent(11.4064, 76.6932), indent=2))