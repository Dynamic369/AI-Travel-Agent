import streamlit as st
from graph import trip_graph
from model import TravelState
import base64
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Agentic Travel Assistant",layout="wide")
st.title("Agentic Travel Assistant")

with st.form("trip_form"):
    city = st.text_input("Destination City",value="Delhi,Ayodhya")
    days = st.number_input("Number of days",min_value=1,max_value=30, value=3)
    interests = st.text_input("Interests (comma-seprated)",value="culture,food")
    budget = st.selectbox("Budget",['low','medium','high'])
    submitted = st.form_submit_button("Generate Itinerary")


    if submitted:
        st.info("Generating itinerary- this may take a moment while LLM LLM and API are called.")
        state = TravelState(
            city = city,
            days=int(days),
            interests=[s.strip() for s in interests.split(",") if s.strip()],
            budget=budget
        )
        result = trip_graph.invoke(state.dict())

        # LangGraph returns a dict-like merged state. Wrap to TravelState for convenience
        # some LangGraph versions return pydantic object; handle both
        if isinstance(result, dict):
            merged = result
        else:
            merged = dict(result)

        if merged.get("error"):
            st.error(merged["error"])
        else:
            # Show itinerary text
            itinerary_text = merged.get("itinerary_text") or "No itinerary produced."
            st.header("Itinerary")
            st.write(itinerary_text)

            pdf_bytes = merged.get("itinerary_pdf_bytes")
            if pdf_bytes:
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="itinerary.pdf">Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

            # If route_plan exists with ordered coords, show map
            route_plan = merged.get("route_plan") or {}
            ordered = route_plan.get("ordered") or []
            if ordered:
                # build folium map
                center = (ordered[0]["lat"], ordered[0]["lon"])
                m = folium.Map(location=center, zoom_start=13)
                for idx, p in enumerate(ordered):
                    folium.Marker([p["lat"], p["lon"]], popup=f"Stop {idx+1}").add_to(m)
                st.subheader("Route Map")
                st_folium(m, width=700, height=450)
