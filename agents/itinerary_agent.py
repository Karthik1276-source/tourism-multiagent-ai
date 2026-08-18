def _time_slot_order(best_time: str) -> int:
    """Map a place's best-visit-time to a sort order for scheduling within a day."""
    order = {"Morning": 0, "Afternoon": 1, "Evening": 2, "Night": 3, "All": 1, "Anytime": 1}
    return order.get(best_time, 1)


def build_itinerary(ranked_destinations: list, num_days: int) -> dict:
    """
    Distribute places across days, grouping by their best-time-to-visit
    (Morning / Afternoon / Evening) so each day flows naturally instead of
    being a random round-robin list.
    """
    itinerary = {f"Day {i+1}": {"Morning": [], "Afternoon": [], "Evening": []} for i in range(num_days)}

    sorted_places = sorted(ranked_destinations, key=lambda p: _time_slot_order(p.get("best_time_to_visit", "All")))

    day_index = 0
    for place in sorted_places:
        day_key = f"Day {(day_index % num_days) + 1}"
        best_time = place.get("best_time_to_visit", "All")

        if best_time == "Morning":
            slot = "Morning"
        elif best_time == "Evening" or best_time == "Night":
            slot = "Evening"
        else:
            slot = "Afternoon"

        itinerary[day_key][slot].append({
            "name": place["name"],
            "avg_visit_hours": place.get("avg_visit_hours", 1.5),
            "entry_fee": place.get("entry_fee", 0),
        })

        # Move to next day once this day has 2+ places, to spread things out
        if sum(len(v) for v in itinerary[day_key].values()) >= 2:
            day_index += 1

    return itinerary


def run_itinerary_agent(ranked_destinations: list, num_days: int) -> dict:
    return build_itinerary(ranked_destinations, num_days)


if __name__ == "__main__":
    import json
    sample = [
        {"name": "Ooty Botanical Garden", "best_time_to_visit": "Morning", "avg_visit_hours": 2, "entry_fee": 50},
        {"name": "Doddabetta Peak", "best_time_to_visit": "Morning", "avg_visit_hours": 1.5, "entry_fee": 20},
        {"name": "Pykara Lake", "best_time_to_visit": "Evening", "avg_visit_hours": 2, "entry_fee": 30},
    ]
    print(json.dumps(run_itinerary_agent(sample, num_days=2), indent=2))