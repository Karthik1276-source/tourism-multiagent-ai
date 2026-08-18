import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_explanation(destination_name: str, score_breakdown: dict, context: dict) -> str:
    """Use an LLM to turn scoring data into a plain-language explanation."""

    prompt = f"""You are a travel assistant. Explain in 1-2 short sentences why
{destination_name} is being recommended, based on this data:

Weather: {context.get('weather')}
Seasonal events: {context.get('seasonal_context')}
Match score: {score_breakdown}

Keep it friendly, specific, and under 40 words. Do not repeat raw numbers."""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Recommended based on your preferences and current conditions. (Explanation generation failed: {e})"


def run_explanation_agent(destination_name: str, score: float, context: dict) -> str:
    return generate_explanation(destination_name, {"score": score}, context)


def generate_trip_summary_explanation(affordable_places: list, breakdown: dict, num_days: int) -> list:
    """
    Generate a bullet-point 'Why this itinerary?' summary — rule-based (not LLM),
    so it's fast, free, and always consistent.
    """
    points = []

    if affordable_places:
        points.append(f"✓ {len(affordable_places)} places selected to match your interests and stay within budget")

    morning_count = sum(1 for p in affordable_places if p.get("best_time_to_visit") == "Morning")
    evening_count = sum(1 for p in affordable_places if p.get("best_time_to_visit") in ["Evening", "Night"])
    if morning_count:
        points.append(f"✓ {morning_count} place(s) scheduled in the morning for the best visiting conditions")
    if evening_count:
        points.append(f"✓ {evening_count} place(s) scheduled in the evening based on typical best-time recommendations")

    if not breakdown.get("over_budget"):
        points.append(f"✓ Estimated total cost (₹{breakdown.get('estimated_total', 0)}) stays within your ₹{breakdown.get('budget_limit', 0)} budget")
    else:
        points.append(f"⚠ Estimated cost (₹{breakdown.get('estimated_total', 0)}) slightly exceeds your ₹{breakdown.get('budget_limit', 0)} budget — consider fewer paid attractions")

    points.append(f"✓ Itinerary spread across {num_days} day(s) to avoid overcrowding any single day")

    return points


if __name__ == "__main__":
    sample_context = {
        "weather": {"success": True, "condition": "Clear"},
        "seasonal_context": {"events": [{"event": "Flower Show", "in_season": True}]},
    }
    print(run_explanation_agent("Ooty Botanical Garden", 0.9, sample_context))