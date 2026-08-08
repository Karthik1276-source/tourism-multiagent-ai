def filter_and_score_by_budget(pois: list, total_budget: float, num_days: int) -> list:
    """
    Filter/annotate POIs based on whether they fit within the trip's budget.
    Assumes total_budget covers entry fees only (extend later for food/transport/stay).
    """
    daily_budget = total_budget / max(num_days, 1)

    annotated = []
    running_total = 0

    sorted_pois = sorted(pois, key=lambda p: p.get("entry_fee", 0))

    for poi in sorted_pois:
        fee = poi.get("entry_fee", 0)
        fits_budget = (running_total + fee) <= total_budget

        annotated.append({
            **poi,
            "entry_fee": fee,
            "fits_budget": fits_budget,
            "running_total_if_included": running_total + fee if fits_budget else running_total,
        })

        if fits_budget:
            running_total += fee

    return annotated


def run_budget_agent(pois: list, total_budget: float, num_days: int) -> dict:
    annotated = filter_and_score_by_budget(pois, total_budget, num_days)
    affordable = [p for p in annotated if p["fits_budget"]]
    total_spent = sum(p["entry_fee"] for p in affordable)

    return {
        "all_places": annotated,
        "affordable_places": affordable,
        "total_estimated_cost": total_spent,
        "budget_remaining": total_budget - total_spent,
    }


if __name__ == "__main__":
    sample = [
        {"name": "Ooty Botanical Garden", "entry_fee": 50},
        {"name": "Doddabetta Peak", "entry_fee": 20},
        {"name": "Pykara Lake", "entry_fee": 30},
    ]
    import json
    print(json.dumps(run_budget_agent(sample, total_budget=60, num_days=2), indent=2))