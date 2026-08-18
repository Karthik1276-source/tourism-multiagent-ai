def filter_and_score_by_budget(pois: list, entry_fee_budget: float, num_days: int) -> list:
    """Filter/annotate POIs based on whether they fit within the entry-fee portion of the budget."""
    annotated = []
    running_total = 0
    sorted_pois = sorted(pois, key=lambda p: p.get("entry_fee", 0))

    for poi in sorted_pois:
        fee = poi.get("entry_fee", 0)
        fits_budget = (running_total + fee) <= entry_fee_budget

        annotated.append({
            **poi,
            "entry_fee": fee,
            "fits_budget": fits_budget,
            "running_total_if_included": running_total + fee if fits_budget else running_total,
        })

        if fits_budget:
            running_total += fee

    return annotated


def estimate_budget_breakdown_scaled(total_budget: float, num_days: int, actual_entry_fees: float, reserved_for_other: float) -> dict:
    """Split reserved budget proportionally across accommodation/food/transport, scaled to fit."""
    ideal_accommodation = 800 * num_days
    ideal_food = 500 * num_days
    ideal_transport = 300 * num_days
    ideal_total = ideal_accommodation + ideal_food + ideal_transport

    scale = reserved_for_other / ideal_total if ideal_total > 0 else 0

    accommodation = ideal_accommodation * scale
    food = ideal_food * scale
    transport = ideal_transport * scale
    activities = actual_entry_fees
    estimated_total = accommodation + food + transport + activities

    return {
        "accommodation": round(accommodation),
        "food": round(food),
        "transport": round(transport),
        "activities": round(activities),
        "miscellaneous": round(max(0, total_budget - estimated_total)),
        "estimated_total": round(estimated_total),
        "budget_limit": round(total_budget),
        "remaining": round(total_budget - estimated_total),
        "over_budget": estimated_total > total_budget,
    }


def run_budget_agent(pois: list, total_budget: float, num_days: int) -> dict:
    """
    total_budget here is the FULL trip budget (not just entry fees).
    Reserve a portion for accommodation/food/transport, but scale it down
    if the budget is tight, so there's always something left for entry fees.
    """
    ideal_reserved = (800 + 500 + 300) * num_days  # accommodation + food + transport

    # Never reserve more than 70% of the total budget — leaves room for entry fees
    max_reserved = total_budget * 0.7
    reserved_for_other_categories = min(ideal_reserved, max_reserved)

    entry_fee_budget = max(0, total_budget - reserved_for_other_categories)

    annotated = filter_and_score_by_budget(pois, entry_fee_budget, num_days)
    affordable = [p for p in annotated if p["fits_budget"]]
    total_spent_on_fees = sum(p["entry_fee"] for p in affordable)

    breakdown = estimate_budget_breakdown_scaled(
        total_budget, num_days, total_spent_on_fees, reserved_for_other_categories
    )

    return {
        "all_places": annotated,
        "affordable_places": affordable,
        "total_estimated_cost": total_spent_on_fees,
        "budget_remaining": entry_fee_budget - total_spent_on_fees,
        "breakdown": breakdown,
    }


if __name__ == "__main__":
    import json
    sample = [
        {"name": "Ooty Botanical Garden", "entry_fee": 50},
        {"name": "Doddabetta Peak", "entry_fee": 20},
        {"name": "Pykara Lake", "entry_fee": 30},
    ]
    print(json.dumps(run_budget_agent(sample, total_budget=5000, num_days=3), indent=2))