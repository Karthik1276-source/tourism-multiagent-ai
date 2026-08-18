import sys
import os
import html
import requests
import streamlit as st
import streamlit.components.v1 as components

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.intent_agent import (
    extract_trip_details,
    merge_details,
    missing_fields_message,
)

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TripMind AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS - TRAVEL AI DASHBOARD
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #030b18;
    --panel: #071426;
    --panel2: #0b1b31;
    --border: rgba(255,255,255,.10);
    --text: #f4f7fb;
    --muted: #8d9aac;
    --blue: #1769ff;
    --cyan: #20b9ff;
    --green: #35d36f;
    --purple: #7b5cff;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: radial-gradient(circle at 75% 10%, rgba(23,105,255,.10), transparent 30%), #030b18 !important;
    color: var(--text) !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

.main .block-container { max-width: 1550px !important; padding: 20px 22px 110px !important; }

[data-testid="stSidebar"] {
    width: 300px !important; min-width: 300px !important;
    background: linear-gradient(180deg, #020a15 0%, #030b18 100%) !important;
    border-right: 1px solid rgba(255,255,255,.08) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 20px !important; }

.sidebar-brand { display: flex; align-items: center; gap: 12px; padding: 5px 5px 25px; }
.brand-icon {
    width: 42px; height: 42px; border-radius: 13px;
    display: flex; align-items: center; justify-content: center; font-size: 22px;
    background: linear-gradient(135deg, #19c7ff, #1769ff 55%, #7358ff);
    box-shadow: 0 0 25px rgba(23,105,255,.35);
}
.brand-name { font-size: 20px; font-weight: 800; }
.brand-name span { color: #2990ff; }
.brand-sub { color: #7f8b9c; font-size: 11px; margin-top: 3px; }

[data-testid="stSidebar"] .stButton > button {
    width: 100% !important; height: 48px !important; border: 0 !important; border-radius: 11px !important;
    background: linear-gradient(110deg, #1dbaff, #1769ff 60%, #555cff) !important;
    color: white !important; font-weight: 700 !important;
    box-shadow: 0 8px 25px rgba(23,105,255,.25) !important;
}

.sidebar-section { color: #758399; font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; margin-top: 30px; margin-bottom: 12px; }
.sidebar-empty { color: #687487; font-size: 13px; padding: 5px; }
.sidebar-tip { margin-top: 30px; padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,.07);
    background: linear-gradient(145deg, #0a1628, #06101d); color: #aeb8c7; font-size: 12px; line-height: 1.6; }

.travel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.travel-logo { display: flex; align-items: center; gap: 10px; }
.travel-logo-icon { font-size: 31px; }
.travel-logo-name { font-size: 23px; font-weight: 800; }
.travel-logo-sub { color: #78879c; font-size: 11px; }

.info-grid { display: grid; grid-template-columns: repeat(4, minmax(130px, 1fr)); gap: 10px; margin-bottom: 15px; }
.info-card { min-height: 70px; display: flex; align-items: center; gap: 12px; padding: 12px 15px; border-radius: 13px;
    border: 1px solid rgba(255,255,255,.07); background: linear-gradient(145deg, #0a192d, #061221); }
.info-icon { font-size: 23px; }
.info-label { color: #7f8da0; font-size: 11px; }
.info-value { color: #f3f6fa; font-size: 15px; font-weight: 700; }

.main-grid { display: grid; grid-template-columns: 300px minmax(450px, 1fr) minmax(400px, 1fr); gap: 12px; align-items: start; }

.panel { border: 1px solid rgba(255,255,255,.08); border-radius: 14px;
    background: linear-gradient(145deg, rgba(9,25,45,.97), rgba(5,15,28,.97)); box-shadow: 0 10px 35px rgba(0,0,0,.22); }
.panel-title { padding: 15px 16px; border-bottom: 1px solid rgba(255,255,255,.07); font-size: 15px; font-weight: 750; }

.chat-panel { min-height: 660px; display: flex; flex-direction: column; }
.chat-body { padding: 12px; flex: 1; max-height: 570px; overflow-y: auto; }
.chat-message { margin-bottom: 12px; }
.chat-ai { background: #0d1c30; border: 1px solid rgba(255,255,255,.06); border-radius: 5px 14px 14px 14px; padding: 11px 13px; color: #e7edf5; font-size: 13px; line-height: 1.55; }
.chat-user { background: linear-gradient(135deg, #0d63ef, #1769ff); border-radius: 14px 5px 14px 14px; padding: 11px 13px; color: white; font-size: 13px; line-height: 1.55; margin-left: 20px; }
.chat-name { color: #65b9ff; font-size: 11px; font-weight: 700; margin-bottom: 5px; }

.preference-box { margin: 12px; padding: 13px; border-radius: 12px; background: #081628; border: 1px solid rgba(255,255,255,.06); }
.preference-title { font-size: 13px; font-weight: 750; margin-bottom: 10px; }
.preference-row { display: flex; align-items: center; gap: 9px; color: #b7c1ce; font-size: 12px; margin: 8px 0; }

.itinerary-panel { min-height: 660px; }
.day-card { margin: 10px; border-radius: 11px; border: 1px solid rgba(255,255,255,.07); background: #08172a; overflow: hidden; }
.day-header { display: flex; justify-content: space-between; padding: 12px 14px; font-weight: 750; border-bottom: 1px solid rgba(255,255,255,.06); }
.day-count { color: #4ca7ff; font-size: 12px; }
.slot-label { color: #6f9bd6; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; padding: 8px 13px 2px; }
.timeline { padding: 5px 13px 10px 18px; }
.timeline-item { position: relative; display: grid; grid-template-columns: 65px 1fr 55px; gap: 8px; align-items: center; min-height: 70px;
    border-left: 2px solid #1769ff; padding-left: 13px; margin-left: 3px; }
.timeline-item::before { content: ""; position: absolute; width: 9px; height: 9px; border-radius: 50%; background: #22a9ff; box-shadow: 0 0 10px rgba(34,169,255,.8); left: -5px; }
.place-thumb { width: 58px; height: 48px; border-radius: 8px; background: linear-gradient(135deg, #123f72, #1769ff); display: flex; align-items: center; justify-content: center; font-size: 22px; }
.place-info-name { color: #f3f6fa; font-size: 13px; font-weight: 750; }
.place-info-desc { color: #7f8da0; font-size: 10px; margin-top: 3px; }
.free-badge { color: #45df7b; background: rgba(53,211,111,.12); padding: 5px 7px; border-radius: 7px; font-size: 9px; text-align: center; }

.map-panel { min-height: 660px; }
.map-fallback { height: 480px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #75859a; text-align: center;
    border-radius: 11px; background: linear-gradient(145deg, #0b2037, #071525); margin: 12px; }
.map-fallback-icon { font-size: 50px; margin-bottom: 10px; }
.route-list { padding: 10px 4px; }
.route-item { display: flex; gap: 9px; align-items: center; margin: 8px 0; font-size: 12px; color: #c8d1dd; }
.route-number { width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: #1769ff; color: white; font-size: 10px; }

.bottom-grid { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin-top: 12px; }
.bottom-card { min-height: 145px; padding: 14px; border-radius: 13px; border: 1px solid rgba(255,255,255,.07);
    background: linear-gradient(145deg, #09192d, #061321); }
.bottom-title { font-size: 13px; font-weight: 750; margin-bottom: 13px; }
.metric-row { display: flex; justify-content: space-between; color: #aeb9c8; font-size: 11px; margin: 8px 0; }
.metric-value { color: #f1f5fa; font-weight: 700; }
.green { color: #42df79 !important; }
.blue { color: #55b1ff !important; }
.progress { width: 100%; height: 7px; border-radius: 20px; background: #17283d; margin-top: 12px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #18c7ff, #1769ff); border-radius: 20px; }

.why-panel { margin-top: 12px; padding: 12px 16px; border-radius: 12px; background: linear-gradient(90deg, #09204a, #081b35);
    border: 1px solid rgba(54,141,255,.18); color: #aebfd4; font-size: 11px; }
.why-title { color: #5eb5ff; font-size: 12px; font-weight: 750; margin-right: 15px; }

[data-testid="stChatInput"] { position: fixed !important; z-index: 999; bottom: 18px !important; left: calc(50% + 145px) !important;
    transform: translateX(-50%); width: min(1000px, calc(100vw - 390px)) !important; }
[data-testid="stChatInput"] > div { border: 1px solid rgba(255,255,255,.12) !important; border-radius: 16px !important;
    background: linear-gradient(145deg, #0d1929, #07101d) !important; box-shadow: 0 15px 45px rgba(0,0,0,.45) !important; }
[data-testid="stChatInput"] textarea { color: white !important; font-size: 14px !important; }
[data-testid="stChatInput"] button { background: linear-gradient(135deg, #19b9ff, #1769ff) !important; border-radius: 50% !important; }

[data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(255,255,255,.06) !important; }

@media(max-width:1200px) {
    .main-grid { grid-template-columns: 280px 1fr; }
    .map-panel { grid-column: 1 / -1; }
    .bottom-grid { grid-template-columns: 1fr 1fr; }
}
@media(max-width:800px) {
    .main-grid { grid-template-columns: 1fr; }
    .info-grid { grid-template-columns: 1fr 1fr; }
    .bottom-grid { grid-template-columns: 1fr; }
    [data-testid="stSidebar"] { width: 240px !important; min-width: 240px !important; }
    [data-testid="stChatInput"] { left: 50% !important; width: calc(100vw - 30px) !important; }
}

</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "trip_details" not in st.session_state:
    st.session_state.trip_details = {}
if "trip_history" not in st.session_state:
    st.session_state.trip_history = []
if "latest_result" not in st.session_state:
    st.session_state.latest_result = None
if "latest_destination" not in st.session_state:
    st.session_state.latest_destination = ""

# ============================================================
# HELPERS
# ============================================================

def safe_text(value):
    return html.escape(str(value or ""))


def get_place_name(place):
    if isinstance(place, str):
        return place
    return place.get("name", "Tourist Place")


def get_place_fee(place):
    if isinstance(place, dict):
        try:
            return float(place.get("entry_fee", 0) or 0)
        except Exception:
            return 0
    return 0


def get_place_emoji(place):
    text = str(place).lower() if isinstance(place, str) else str(place.get("name", "")).lower()
    if "beach" in text: return "🌊"
    if "fort" in text: return "🏰"
    if "temple" in text or "church" in text or "basilica" in text: return "⛪"
    if "waterfall" in text: return "💦"
    if "museum" in text: return "🏛️"
    if "park" in text or "garden" in text: return "🌴"
    return "📍"

# ============================================================
# HEADER DATA
# ============================================================

destination = st.session_state.latest_destination or st.session_state.trip_details.get("destination") or "Not set"
days = st.session_state.trip_details.get("num_days") or 0
budget = st.session_state.trip_details.get("total_budget") or 0

st.markdown(
    """
<div class="travel-header">
    <div class="travel-logo">
        <div class="travel-logo-icon">🌴</div>
        <div>
            <div class="travel-logo-name">TripMind <span>AI</span></div>
            <div class="travel-logo-sub">Your AI Travel Planner</div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="info-grid">
    <div class="info-card"><div class="info-icon">📍</div>
        <div><div class="info-label">Destination</div><div class="info-value">{safe_text(destination)}</div></div></div>
    <div class="info-card"><div class="info-icon">📅</div>
        <div><div class="info-label">Duration</div><div class="info-value">{days} Days</div></div></div>
    <div class="info-card"><div class="info-icon">💳</div>
        <div><div class="info-label">Budget</div><div class="info-value">₹{float(budget):,.0f}</div></div></div>
    <div class="info-card"><div class="info-icon">🎒</div>
        <div><div class="info-label">Travel Style</div><div class="info-value">Budget</div></div></div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
<div class="sidebar-brand">
    <div class="brand-icon">✈</div>
    <div><div class="brand-name">TripMind <span>AI</span></div>
    <div class="brand-sub">Context-aware travel planner</div></div>
</div>
""",
        unsafe_allow_html=True,
    )

    if st.button("＋  New Trip", use_container_width=True):
        st.session_state.messages = []
        st.session_state.trip_details = {}
        st.session_state.latest_result = None
        st.session_state.latest_destination = ""
        st.rerun()

    st.markdown('<div class="sidebar-section">Recent Trips</div>', unsafe_allow_html=True)

    if st.session_state.trip_history:
        for i, trip in enumerate(st.session_state.trip_history):
            st.button(f"📍 {trip}", key=f"history_{i}", use_container_width=True)
    else:
        st.markdown('<div class="sidebar-empty">No trips planned yet</div>', unsafe_allow_html=True)

    st.markdown(
        """
<div class="sidebar-tip">
<b style="color:#55b8ff;">💡 Smart Planning</b><br><br>
Tell me:<br>• Destination<br>• Number of days<br>• Budget<br>• Interests<br><br>
I'll generate a personalized time + budget optimized itinerary.
</div>
""",
        unsafe_allow_html=True,
    )

# ============================================================
# RESULT DATA
# ============================================================

result = st.session_state.latest_result

st.markdown('<div class="main-grid">', unsafe_allow_html=True)

# ============================================================
# LEFT - AI CHAT
# ============================================================

st.markdown(
    """
<div class="panel chat-panel">
<div class="panel-title">🤖 AI Trip Planner</div>
<div class="chat-body">
""",
    unsafe_allow_html=True,
)

if not st.session_state.messages:
    st.markdown(
        """
<div class="chat-message">
<div class="chat-name">TripMind AI</div>
<div class="chat-ai">Hello! 👋<br><br>I'm your AI travel assistant.<br><br>
Tell me where you want to go, how many days you're travelling, your budget and interests.</div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state.messages:
        role = msg.get("role")
        content = safe_text(msg.get("content", "")).replace("\n", "<br>")
        if role == "user":
            st.markdown(f'<div class="chat-message"><div class="chat-user">{content}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="chat-message"><div class="chat-name">TripMind AI</div><div class="chat-ai">{content}</div></div>',
                unsafe_allow_html=True,
            )

# ---------- Preferences box ----------
details = st.session_state.trip_details
interests = details.get("interests") or []
interests_text = ", ".join(interests) if isinstance(interests, list) and interests else "Not specified"

st.markdown(
    f"""
<div class="preference-box">
<div class="preference-title">🎯 Extracted Preferences</div>
<div class="preference-row">📍 Destination: <b>{safe_text(destination)}</b></div>
<div class="preference-row">📅 Duration: <b>{days} Days</b></div>
<div class="preference-row">💰 Budget: <b>Under ₹{float(budget):,.0f}</b></div>
<div class="preference-row">❤️ Interests: <b>{safe_text(interests_text)}</b></div>
<div class="preference-row">🎒 Style: <b>Budget Travel</b></div>
</div>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# CENTER - ITINERARY  (now includes Google Maps navigation buttons)
# ============================================================

st.markdown('<div class="panel itinerary-panel"><div class="panel-title">📅 Day-by-day Itinerary</div>', unsafe_allow_html=True)


def render_itinerary(result):
    itinerary = result.get("itinerary", {})

    if not isinstance(itinerary, dict) or not itinerary:
        st.info("Itinerary will appear here after the AI generates your trip.")
        return

    for day, slots in itinerary.items():
        if not isinstance(slots, dict):
            continue

        total_places = sum(len(v) for v in slots.values())

        st.markdown(
            f"""
<div class="day-card">
<div class="day-header"><span>{safe_text(day)}</span><span class="day-count">{total_places} Places</span></div>
""",
            unsafe_allow_html=True,
        )

        for slot_name in ["Morning", "Afternoon", "Evening"]:
            places = slots.get(slot_name, [])
            if not places:
                continue

            st.markdown(f'<div class="slot-label">{slot_name}</div><div class="timeline">', unsafe_allow_html=True)

            for place in places:
                name = get_place_name(place)
                fee = get_place_fee(place)
                hours = place.get("avg_visit_hours", 1.5) if isinstance(place, dict) else 1.5
                emoji = get_place_emoji(place)
                fee_text = "FREE" if fee == 0 else f"₹{fee:.0f}"
                maps_url = place.get("google_maps_url") if isinstance(place, dict) else None

                st.markdown(
                    f"""
<div class="timeline-item">
<div class="place-thumb">{emoji}</div>
<div>
<div class="place-info-name">{safe_text(name)}</div>
<div class="place-info-desc">~{hours}h visit</div>
</div>
<div class="free-badge">{fee_text}</div>
</div>
""",
                    unsafe_allow_html=True,
                )

                if maps_url:
                    st.link_button(f"📍 Navigate to {name}", maps_url, key=f"nav_{day}_{slot_name}_{name}")

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


if result and "error" not in result:
    render_itinerary(result)
elif result and "error" in result:
    st.warning(result["error"])
else:
    st.markdown(
        """
<div style="padding:70px 20px;text-align:center;color:#65758a;">
<div style="font-size:45px;">🧳</div><br>
<b style="color:#aab7c8;">Your personalized itinerary will appear here</b><br><br>
Start by typing something like:<br>
<span style="color:#55b4ff;">"Plan a 5 day Goa trip under ₹10,000"</span>
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# RIGHT - MAP  (uses a real st.container so the iframe renders inside the panel)
# ============================================================

map_places = []
if result and "error" not in result:
    for p in result.get("affordable_places", []):
        if not isinstance(p, dict):
            continue
        lat = p.get("latitude")
        lon = p.get("longitude")
        if lat and lon:
            try:
                map_places.append({"name": get_place_name(p), "lat": float(lat), "lon": float(lon)})
            except Exception:
                pass

map_panel = st.container(border=True)

with map_panel:
    st.markdown('<div class="panel-title">🗺️ Trip Route Overview</div>', unsafe_allow_html=True)

    if map_places:
        markers = ""
        for p in map_places:
            markers += f"""
            L.marker([{p['lat']}, {p['lon']}]).addTo(map).bindPopup("<b>{html.escape(p['name'])}</b>");
            """

        points = [[p["lat"], p["lon"]] for p in map_places]
        center_lat = sum(x[0] for x in points) / len(points)
        center_lon = sum(x[1] for x in points) / len(points)

        map_html = f"""
<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>html,body,#map {{ height:100%; margin:0; }} #map {{ border-radius:10px; }}</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map = L.map("map").setView([{center_lat}, {center_lon}], 11);
L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
    maxZoom: 19, attribution: "© OpenStreetMap contributors"
}}).addTo(map);
{markers}
</script>
</body>
</html>
"""
        components.html(map_html, height=480)
    else:
        st.markdown(
            """
<div class="map-fallback">
<div class="map-fallback-icon">🗺️</div>
<b style="color:#aab7c8;">Trip route map</b><br>
Map markers will appear once your trip is planned.<br><br>
<span style="font-size:11px;">OpenStreetMap + Leaflet</span>
</div>
""",
            unsafe_allow_html=True,
        )

    if map_places:
        st.markdown('<div class="route-list">', unsafe_allow_html=True)
        for i, p in enumerate(map_places):
            st.markdown(
                f'<div class="route-item"><div class="route-number">{i + 1}</div><div>{safe_text(p["name"])}</div></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # closes main-grid

# ============================================================
# BOTTOM DASHBOARD — real budget breakdown from backend
# ============================================================

st.markdown("<div style='grid-column:1/-1;'>", unsafe_allow_html=True)

breakdown = {}
if result and "error" not in result:
    breakdown = result.get("budget_breakdown", {})

accommodation = breakdown.get("accommodation", 0)
food = breakdown.get("food", 0)
transport = breakdown.get("transport", 0)
activities = breakdown.get("activities", 0)
misc = breakdown.get("miscellaneous", 0)
estimated_total = breakdown.get("estimated_total", 0)
budget_limit = breakdown.get("budget_limit", float(budget))
remaining = breakdown.get("remaining", float(budget) - estimated_total)
pct_used = min(100, (estimated_total / budget_limit * 100) if budget_limit > 0 else 0)

st.markdown(
    f"""
<div class="bottom-grid">

<div class="bottom-card">
<div class="bottom-title">💰 Budget Summary</div>
<div class="metric-row"><span>Total Budget</span><span class="metric-value green">₹{budget_limit:,.0f}</span></div>
<div class="metric-row"><span>Estimated Cost</span><span class="metric-value blue">₹{estimated_total:,.0f}</span></div>
<div class="metric-row"><span>Remaining</span><span class="metric-value green">₹{remaining:,.0f}</span></div>
<div class="progress"><div class="progress-fill" style="width:{pct_used}%;"></div></div>
<div style="font-size:10px;color:#75859a;margin-top:7px;">{pct_used:.0f}% of budget used</div>
</div>

<div class="bottom-card">
<div class="bottom-title">🏨 Stay Plan</div>
<div class="metric-row"><span>Nights</span><span class="metric-value">{max(1, int(days) - 1) if days else 0}</span></div>
<div class="metric-row"><span>Estimated</span><span class="metric-value blue">₹{accommodation:,.0f}</span></div>
<div style="color:#718096;font-size:10px;margin-top:12px;">Budget-friendly accommodation estimate based on trip duration.</div>
</div>

<div class="bottom-card">
<div class="bottom-title">🍛 Food Plan</div>
<div class="metric-row"><span>Estimated total</span><span class="metric-value blue">₹{food:,.0f}</span></div>
<div style="color:#718096;font-size:10px;margin-top:12px;">Based on typical daily food cost × trip duration.</div>
</div>

<div class="bottom-card">
<div class="bottom-title">🛵 Transport & Activities</div>
<div class="metric-row"><span>Transport</span><span class="metric-value">₹{transport:,.0f}</span></div>
<div class="metric-row"><span>Entry fees</span><span class="metric-value">₹{activities:,.0f}</span></div>
<div class="metric-row"><span>Misc</span><span class="metric-value green">₹{misc:,.0f}</span></div>
</div>

</div>
""",
    unsafe_allow_html=True,
)

# ============================================================
# WHY THIS ITINERARY — real trip_summary from backend
# ============================================================

trip_summary = []
if result and "error" not in result:
    trip_summary = result.get("trip_summary", [])

if trip_summary:
    why_text = " &nbsp; | &nbsp; ".join(safe_text(point) for point in trip_summary)
else:
    why_text = "Plan a trip to see personalized reasoning here."

st.markdown(
    f"""
<div class="why-panel">
<span class="why-title">⭐ Why this itinerary?</span>
{why_text}
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input("Plan a trip, change your budget, or tell me your preferences...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    context_str = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages[-8:])

    with st.spinner("🤖 TripMind AI is understanding your request..."):
        try:
            extracted = extract_trip_details(user_input, context_str)
            st.session_state.trip_details = merge_details(st.session_state.trip_details, extracted)
            details = st.session_state.trip_details
        except Exception:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I couldn't understand the trip details. Please tell me the destination, number of days and budget.",
            })
            st.rerun()

    if not details.get("ready_to_search"):
        follow_up = missing_fields_message(details)
        reply = follow_up if follow_up else "Tell me a little more about your trip."
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    payload = {
        "destination": details.get("destination"),
        "state": details.get("state") or "Unknown",
        "origin_place": details.get("origin_place") or details.get("destination"),
        "preferences": {"interests": details.get("interests") or [], "budget": "medium"},
        "total_budget": details.get("total_budget"),
        "num_days": details.get("num_days"),
        "home_language": details.get("home_language") or "English",
        "destination_language": details.get("destination_language") or "English",
    }

    with st.spinner("🤖 Multi-Agent AI is planning your trip..."):
        try:
            response = requests.post("http://127.0.0.1:8000/recommend", json=payload, timeout=120)
        except requests.RequestException:
            response = None

    if response is None:
        st.session_state.messages.append({
            "role": "assistant",
            "content": "I couldn't connect to the TripMind backend. Make sure FastAPI is running on http://127.0.0.1:8000",
        })
        st.rerun()

    if response.status_code != 200:
        st.session_state.messages.append({
            "role": "assistant", "content": f"Backend returned HTTP {response.status_code}.",
        })
        st.rerun()

    try:
        result = response.json()
    except ValueError:
        result = {"error": "Backend returned invalid JSON."}

    if result.get("error"):
        st.session_state.messages.append({"role": "assistant", "content": str(result["error"])})
        st.rerun()

    destination_final = details.get("destination") or "your destination"

    st.session_state.latest_result = result
    st.session_state.latest_destination = destination_final
    st.session_state.trip_details = details

    if destination_final not in st.session_state.trip_history:
        st.session_state.trip_history.append(destination_final)

    st.session_state.messages.append({
        "role": "assistant",
        "content": f"Great! I created your {details.get('num_days', '')}-day personalized trip to {destination_final}.",
    })

    st.rerun()