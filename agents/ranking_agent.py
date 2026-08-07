def score_destination(destination: dict, preferences: dict, context: dict) -> float:
    """
    Score a destination based on user preferences and context signals.
    destination: {"name": ..., "tags": [...], "budget_level": ...}
    preferences: {"interests": [...], "budget": ..., "travel_with": ...}
    context: output from context_agent (weather, seasonal_context)
    """
    score = 0.0

    # Preference match (40%)
    matched_tags = set(destination.get("tags", [])) & set(preferences.get("interests", []))
    preference_score = len(matched_tags) / max(len(preferences.get("interests", [])), 1)
    score += preference_score * 0.4

    # Seasonal fit (30%)
    seasonal_score = 0
    for event in context.get("seasonal_context", {}).get("events", []):
        if event.get("in_season"):
            seasonal_score = 1
            break
    score += seasonal_score * 0.3

    # Weather suitability (30%)
    weather = context.get("weather", {})
    weather_score = 0.5  # neutral default
    if weather.get("success"):
        condition = weather.get("condition", "").lower()
        if condition in ["clear", "clouds"]:
            weather_score = 1.0
        elif condition in ["rain", "thunderstorm", "snow"]:
            weather_score = 0.2
    score += weather_score * 0.3

    return round(score, 3)


def run_ranking_agent(destinations: list, preferences: dict, context: dict) -> list:
    """Rank a list of destinations, highest score first."""
    ranked = []
    for dest in destinations:
        s = score_destination(dest, preferences, context)
        ranked.append({**dest, "score": s})

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


if __name__ == "__main__":
    sample_destinations = [
        {"name": "Ooty Botanical Garden", "tags": ["nature", "family"]},
        {"name": "Doddabetta Peak", "tags": ["nature", "adventure"]},
    ]
    sample_prefs = {"interests": ["nature", "family"], "budget": "medium"}
    sample_context = {
        "weather": {"success": True, "condition": "Clear"},
        "seasonal_context": {"events": [{"in_season": True}]},
    }
    print(run_ranking_agent(sample_destinations, sample_prefs, sample_context))