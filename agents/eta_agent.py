from datetime import datetime, timedelta


def calculate_eta(duration_minutes: float, start_time: datetime = None) -> dict:
    """
    Convert a travel duration into an actual clock arrival time.
    If start_time isn't given, assumes 'starting now'.
    """
    if start_time is None:
        start_time = datetime.now()

    arrival_time = start_time + timedelta(minutes=duration_minutes)

    return {
        "start_time": start_time.strftime("%I:%M %p"),
        "arrival_time": arrival_time.strftime("%I:%M %p"),
        "duration_minutes": round(duration_minutes),
    }


def calculate_eta_from_speed(distance_km: float, speed_kmph: float, start_time: datetime = None) -> dict:
    """
    Recompute ETA based on a user-specified average speed instead of the API's default estimate.
    Useful for hill routes, traffic-heavy areas, or a traveler's own driving pace.
    """
    if speed_kmph <= 0:
        return {"success": False, "error": "Speed must be greater than 0"}

    duration_hours = distance_km / speed_kmph
    duration_minutes = duration_hours * 60

    eta = calculate_eta(duration_minutes, start_time)
    eta["success"] = True
    eta["assumed_speed_kmph"] = speed_kmph
    eta["distance_km"] = distance_km

    return eta


def run_eta_agent(distance_km: float, default_duration_minutes: float, custom_speed_kmph: float = None) -> dict:
    """
    Main entry point. If custom_speed_kmph is provided, recompute ETA using that speed.
    Otherwise use the default duration from the travel-time agent (API-estimated).
    """
    if custom_speed_kmph:
        return calculate_eta_from_speed(distance_km, custom_speed_kmph)
    else:
        result = calculate_eta(default_duration_minutes)
        result["success"] = True
        result["assumed_speed_kmph"] = None
        result["distance_km"] = distance_km
        return result


if __name__ == "__main__":
    import json
    # Example: 42 km away, API estimates 60 minutes at default traffic speed
    print("Default estimate:")
    print(json.dumps(run_eta_agent(distance_km=42, default_duration_minutes=60), indent=2))

    print("\nUser-specified speed (30 km/h, hill roads):")
    print(json.dumps(run_eta_agent(distance_km=42, default_duration_minutes=60, custom_speed_kmph=30), indent=2))