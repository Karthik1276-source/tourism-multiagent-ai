import streamlit as st
import requests

st.title("🧭 Context-Based Tourism Recommendation")

destination = st.text_input("Destination", "Ooty")
state = st.text_input("Destination State", "Tamil Nadu")
num_days = st.slider("Trip duration (days)", 1, 10, 3)
interests = st.multiselect("Interests", ["nature", "adventure", "heritage", "spiritual", "family"], default=["nature"])
home_language = st.text_input("Your home language", "Tamil")
dest_language = st.text_input("Destination language", "Tamil")

if st.button("Get Recommendations"):
    payload = {
        "destination": destination,
        "state": state,
        "candidate_places": [
            {"name": "Ooty Botanical Garden", "tags": ["nature", "family"]},
            {"name": "Doddabetta Peak", "tags": ["nature", "adventure"]},
        ],
        "preferences": {"interests": interests, "budget": "medium"},
        "num_days": num_days,
        "home_language": home_language,
        "destination_language": dest_language,
    }

    with st.spinner("Running agents..."):
        response = requests.post("http://127.0.0.1:8000/recommend", json=payload)

    if response.status_code == 200:
        result = response.json()

        st.subheader("Ranked Places")
        for place in result["ranked_places"]:
            st.write(f"**{place['name']}** — score: {place['score']}")
            st.caption(result["explanations"].get(place["name"], ""))

        st.subheader("Itinerary")
        st.json(result["itinerary"])

        st.subheader("Cultural & Language Notes")
        st.json(result["culture_language"])
    else:
        st.error("Something went wrong calling the backend.")