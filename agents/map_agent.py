def google_maps_directions_url(dest_lat: float, dest_lon: float, origin_lat: float = None, origin_lon: float = None) -> str:
    """
    Build a Google Maps URL that opens turn-by-turn navigation directly.
    No API key needed — this is just Google's public URL scheme.
    """
    base = "https://www.google.com/maps/dir/?api=1"
    destination = f"&destination={dest_lat},{dest_lon}"

    if origin_lat is not None and origin_lon is not None:
        origin = f"&origin={origin_lat},{origin_lon}"
    else:
        origin = ""  # Google Maps will use the user's current location automatically

    return f"{base}{origin}{destination}&travelmode=driving"


def google_maps_search_url(place_name: str, city: str) -> str:
    """Fallback: a simple 'search this place' link when we don't have exact coordinates."""
    query = f"{place_name}, {city}".replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={query}"