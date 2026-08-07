def build_itinerary(ranked_destinations: list, num_days: int) -> dict:
    """
    Distribute top-ranked destinations across the trip days.
    Simple version: round-robin assignment, 1-2 spots per day.
    """
    itinerary = {f"Day {i+1}": [] for i in range(num_days)}
    spots_per_day = max(1, len(ranked_destinations) // num_days)

    day_index = 0
    for i, dest in enumerate(ranked_destinations):
        day_key = f"Day {(day_index % num_days) + 1}"
        itinerary[day_key].append(dest["name"])
        if (i + 1) % spots_per_day == 0:
            day_index += 1

    return itinerary


def run_itinerary_agent(ranked_destinations: list, num_days: int) -> dict:
    return build_itinerary(ranked_destinations, num_days)


if __name__ == "__main__":
    sample = [
        {"name": "Ooty Botanical Garden", "score": 0.9},
        {"name": "Doddabetta Peak", "score": 0.75},
        {"name": "Pykara Lake", "score": 0.6},
    ]
    print(run_itinerary_agent(sample, num_days=2))