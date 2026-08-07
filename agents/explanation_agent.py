import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

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
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Recommended based on your preferences and current conditions. (Explanation generation failed: {e})"


def run_explanation_agent(destination_name: str, score: float, context: dict) -> str:
    return generate_explanation(destination_name, {"score": score}, context)


if __name__ == "__main__":
    sample_context = {
        "weather": {"success": True, "condition": "Clear"},
        "seasonal_context": {"events": [{"event": "Flower Show", "in_season": True}]},
    }
    print(run_explanation_agent("Ooty Botanical Garden", 0.9, sample_context))