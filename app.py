import streamlit as st
from graph import trip_graph
from model import TravelState
import base64
import folium
from streamlit_folium import st_folium
import pandas as pd
from src.utils.cache import install_http_cache

st.set_page_config(page_title="Agentic Travel Assistant",layout="wide")
# install HTTP response cache if available
install_http_cache(cache_name="http_cache", expire_seconds=24*3600)
st.title("Agentic Travel Assistant",width="stretch")

with st.form("trip_form"):
    city = st.text_input("Destination City",value="Jaipur,Ayodhya")
    days = st.number_input("Number of days",min_value=1,max_value=30, value=3)
    interests = st.text_input("Interests (comma-seprated)",value="culture,food")
    budget = st.selectbox("Budget",['low','medium','high'])
    submitted = st.form_submit_button("Generate Itinerary")


    if submitted:
        with st.spinner(text="Generating....", show_time=True):
            state = TravelState(
                city = city,
                days=int(days),
                interests=[s.strip() for s in interests.split(",") if s.strip()],
                budget=budget
            )
            result = trip_graph.invoke(state.model_dump())

            # LangGraph returns a dict-like merged state. Wrap to TravelState for convenience
            # some LangGraph versions return pydantic object; handle both
            if isinstance(result, dict):
                merged = result
            else:
                merged = dict(result)

            if merged.get("error"):
                st.error(merged["error"])
            else:
                # Tabs for better presentation
                tab_itin, tab_map, tab_weather, tab_pois = st.tabs(["Plan", "🗺️ Map", "🌤️ Weather", "Attractions"])

                with tab_itin:
                    itinerary_text = merged.get("itinerary_text") or "No itinerary produced."
                    st.subheader("Your Itinerary")
                    st.markdown(itinerary_text)
                    pdf_bytes = merged.get("itinerary_pdf_bytes")
                    cols = st.columns([1,1])
                    with cols[0]:
                        if pdf_bytes:
                            b64 = base64.b64encode(pdf_bytes).decode()
                            href = f'<a href="data:application/octet-stream;base64,{b64}" download="itinerary.pdf">⬇️ Download PDF</a>'
                            st.markdown(href, unsafe_allow_html=True)
                    with cols[1]:
                        st.caption("Tip: Adjust interests for alternate plans.")

                with tab_map:
                    route_plan = merged.get("route_plan") or {}
                    ordered = route_plan.get("ordered") or []
                    if ordered:
                        center = (ordered[0]["lat"], ordered[0]["lon"])
                        m = folium.Map(location=center, zoom_start=13)
                        for idx, p in enumerate(ordered):
                            folium.Marker([p["lat"], p["lon"]], popup=f"Stop {idx+1}").add_to(m)
                        st_folium(m, width=750, height=500)
                    else:
                        st.info("Route will appear here once attractions are available.")

                with tab_weather:
                    daily = merged.get("weather_data") or {}
                    if daily and isinstance(daily, dict) and daily.get("time"):
                        # Build a friendly daily forecast table
                        def code_to_emoji_desc(code: int):
                            mapping = [
                                (lambda c: c == 0, ("☀️", "Clear")),
                                (lambda c: c in (1, 2, 3), ("⛅", "Partly cloudy")),
                                (lambda c: c in (45, 48), ("🌫️", "Fog")),
                                (lambda c: c in (51, 53, 55), ("🌦️", "Drizzle")),
                                (lambda c: c in (61, 63, 65, 80, 81, 82), ("🌧️", "Rain")),
                                (lambda c: c in (66, 67), ("🌧️🥶", "Freezing rain")),
                                (lambda c: c in (71, 73, 75, 77, 85, 86), ("❄️", "Snow")),
                                (lambda c: c == 95, ("⛈️", "Thunderstorm")),
                                (lambda c: c in (96, 99), ("⛈️🌨️", "Thunderstorm w/ hail")),
                            ]
                            for pred, val in mapping:
                                if pred(code):
                                    return val
                            return ("🌤️", "Weather")

                        times = daily.get("time", [])
                        tmax = daily.get("temperature_2m_max", [])
                        tmin = daily.get("temperature_2m_min", [])
                        wcode = daily.get("weathercode", [])

                        rows = []
                        for i in range(min(len(times), len(tmax), len(tmin), len(wcode))):
                            emoji, desc = code_to_emoji_desc(int(wcode[i]))
                            rows.append({
                                "date": times[i],
                                "max °C": tmax[i],
                                "min °C": tmin[i],
                                "weather": f"{emoji} {desc}",
                            })
                        df = pd.DataFrame(rows)

                        # Show compact cards for next few days
                        st.subheader("Daily forecast")
                        cols = st.columns(min(5, len(df))) if len(df) else []
                        for i, col in enumerate(cols):
                            with col:
                                r = df.iloc[i]
                                st.markdown(f"**{r['date']}**")
                                st.markdown(r["weather"]) 
                                st.metric("Max", f"{r['max °C']:.1f} °C", delta=None)
                                st.caption(f"Min: {r['min °C']:.1f} °C")

                        # Line chart for temps
                        st.markdown("\n")
                        chart_df = df.set_index("date")[ ["max °C", "min °C"] ]
                        st.line_chart(chart_df)

                        # Full table
                        with st.expander("See full forecast table"):
                            st.dataframe(df, use_container_width=True)
                    else:
                        st.info("Weather will appear here when available.")

                with tab_pois:
                    attractions = merged.get("attractions") or []
                    if attractions:
                        show = [{"name": a.get("name"), "kinds": a.get("kinds"), "lat": a.get("lat"), "lon": a.get("lon")} for a in attractions[:10]]
                        st.dataframe(show, use_container_width=True)
                    else:
                        st.info("Attractions will appear here once loaded.")
