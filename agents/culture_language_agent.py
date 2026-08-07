CULTURAL_NOTES = {
    "Tamil Nadu": {
        "etiquette": "Dress modestly at temples; footwear must be removed before entry.",
        "food_note": "Vegetarian food is widely available; meals often served on banana leaves.",
    },
    "Uttarakhand": {
        "etiquette": "Cover your head at Sikh gurdwaras; modest dress expected at temples and ashrams.",
        "food_note": "Pure-vegetarian eateries are common near pilgrimage towns like Rishikesh and Haridwar.",
    },
    "Meghalaya": {
        "etiquette": "Respect local tribal customs; ask before photographing people.",
        "food_note": "Non-vegetarian food is common; vegetarian options exist but are less dominant.",
    },
}

PHRASEBOOK = {
    ("Tamil", "Hindi"): {
        "Thank you": "Dhanyavaad",
        "How much?": "Kitna hai?",
        "Where is...?": "...kahaan hai?",
    }
}


def get_cultural_notes(state: str) -> dict:
    return CULTURAL_NOTES.get(state, {"etiquette": "General respectful conduct advised.", "food_note": "N/A"})


def get_phrasebook(home_language: str, destination_language: str) -> dict:
    return PHRASEBOOK.get((home_language, destination_language), {})


def run_culture_language_agent(state: str, home_language: str, destination_language: str) -> dict:
    return {
        "cultural_notes": get_cultural_notes(state),
        "phrasebook": get_phrasebook(home_language, destination_language),
    }


if __name__ == "__main__":
    print(run_culture_language_agent("Uttarakhand", "Tamil", "Hindi"))