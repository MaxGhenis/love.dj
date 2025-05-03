# app.py
import streamlit as st
from src.ui.streamlit_app import setup_ui, display_results
from src.models.simulation import run_date

# Set up the UI
ui_inputs = setup_ui()

# Run the simulation when the button is clicked
if ui_inputs["go"]:
    try:
        # Display the model being used for debugging
        st.info(f"Using model: {ui_inputs['model_name']}")
        
        with st.spinner("Mixing…"):
            transcript, score_a, score_b = run_date(
                ui_inputs["profile_a"], 
                ui_inputs["profile_b"],
                ui_inputs["name_a"],
                ui_inputs["name_b"],
                ui_inputs["rounds"], 
                ui_inputs["model_name"],
                ui_inputs["theme"]
            )
        
        # Display the results
        display_results(transcript, score_a, score_b, ui_inputs["name_a"], ui_inputs["name_b"], ui_inputs["model_name"])
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Try using a different model or refreshing the page.")
