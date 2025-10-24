import streamlit as st
from src.core.planner import TravelPlanner
from dotenv import load_dotenv
st.set_page_config(page_title="AI Travel Planner",page_icon="✈️")
st.title("AI Travel Planner")
st.write("Plan you trip by simply giving the city and interests.")


load_dotenv()
with st.form("planner_form"):
    city=st.text_input("Enter the city name for your trip")
    interests = st.text_input("Enter your interests but in comma seperated.")
    submitted=st.form_submit_button("Generate itinerary")

    if submitted:
        if city and interests:
            planner= TravelPlanner()
            planner.set_city(city)
            planner.set_interests(interests)
            itinerary = planner.create_itinerary()

            st.subheader("📄 Your Itinerary")
            st.markdown(itinerary)

        else:
            st.warning("Please fill the city and interests to move forward.")