import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.title("🧭 Context-Based Tourism Recommendation")

destination = st.text_input("Destination Area (e.g. Ooty)", "Ooty")
state = st.text_input("Destination State", "Tamil Nadu")
origin_place = st.text_input("Your starting point within the area (e.g. bus stand, hotel)", "Ooty Bus Stand")
num_days = st.slider("Trip duration (days)", 1, 10, 3)
total_budget = st.number_input("Total budget for entry fees (₹)", min_value=0, value=200, step=10)
interests = st.multiselect("Interests", ["nature", "adventure", "heritage", "spiritual", "family"], default=["nature"])
home_language = st.text_input("Your home language", "Tamil")
dest_language = st.text_input("Destination language", "Tamil")

if st.button("Get Recommendations"):
    payload = {
        "destination": destination,
        "state": state,
        "origin_place": origin_place,
        "preferences": {"interests": interests, "budget": "medium"},
        "total_budget": total_budget,
        "num_days": num_days,
        "home_language": home_language,
        "destination_language": dest_language,
    }

    with st.spinner("Running agents..."):
        response = requests.post("http://127.0.0.1:8000/recommend", json=payload)

    if response.status_code == 200:
        st.session_state["result"] = response.json()
        st.session_state["origin_place"] = origin_place
    else:
        st.session_state["result"] = None
        st.error("Something went wrong calling the backend.")
        st.text(response.text)

# Render results from session_state — persists across Streamlit re-runs
if st.session_state.get("result"):
    result = st.session_state["result"]
    origin_place = st.session_state.get("origin_place", "")

    if "error" in result:
        st.error(result["error"])
    else:
        st.subheader(f"Places within budget (₹{result['total_estimated_cost']} spent, ₹{result['budget_remaining']} remaining)")

        valid_places = [p for p in result["affordable_places"] if p.get("latitude") and p.get("longitude")]

        if valid_places:
            avg_lat = sum(p["latitude"] for p in valid_places) / len(valid_places)
            avg_lon = sum(p["longitude"] for p in valid_places) / len(valid_places)

            trip_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)

            for place in valid_places:
                popup_text = f"{place['name']}<br>Entry: ₹{place['entry_fee']}"
                folium.Marker(
                    location=[place["latitude"], place["longitude"]],
                    popup=popup_text,
                    tooltip=place["name"],
                    icon=folium.Icon(color="red", icon="info-sign"),
                ).add_to(trip_map)

            st_folium(trip_map, width=700, height=450, key="trip_map")

        for place in result["affordable_places"]:
            travel = place.get("travel", {})
            if travel.get("success"):
                travel_str = f"{travel['duration_minutes']} min ({travel['distance_km']} km) from {origin_place}"
            else:
                travel_str = "Travel time unavailable"

            st.write(f"**{place['name']}** — Entry: ₹{place['entry_fee']} — {travel_str}")
            st.caption(result["explanations"].get(place["name"], ""))

            if place.get("google_maps_url"):
                st.link_button("📍 Open in Google Maps", place["google_maps_url"])

            st.divider()

        st.subheader("Itinerary")
        st.json(result["itinerary"])

        st.subheader("Nearby Hotels, Hospitals & Pharmacies")
        amenities = result.get("amenities", {})

        if not amenities.get("success"):
            st.info("Amenity data unavailable right now.")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**🏨 Hotels**")
                for h in amenities["hotels"]:
                    st.write(f"- {h['name']}")
                if not amenities["hotels"]:
                    st.caption("None found nearby.")

            with col2:
                st.markdown("**🏥 Hospitals**")
                for h in amenities["hospitals"]:
                    st.write(f"- {h['name']}")
                if not amenities["hospitals"]:
                    st.caption("None found nearby.")

            with col3:
                st.markdown("**💊 Pharmacies**")
                for p in amenities["pharmacies"]:
                    st.write(f"- {p['name']}")
                if not amenities["pharmacies"]:
                    st.caption("None found nearby.")

            st.caption("Note: Ratings aren't available from this free data source — results are shown by proximity, not rating.")

        st.subheader("Cultural & Language Notes")
        st.json(result["culture_language"])

        with st.expander("See all places (including ones over budget)"):
            st.json(result["all_places_with_travel_and_budget"])