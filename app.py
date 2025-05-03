# app.py
import streamlit as st
from src.ui.streamlit_app import setup_ui, display_results
from src.models.simulation import run_date

# Set up the UI
ui_inputs = setup_ui()

# Run the simulation when the button is clicked
if ui_inputs["go"]:
    # Get the model name the user entered
    model_name = ui_inputs["model_name"].strip()
    
    try:
        # Check if model name is empty
        if not model_name:
            model_name = "gpt-4o"  # Default to gpt-4o if empty
            st.warning("No model specified, using gpt-4o as default.")
            
        # Display model and service information
        service_info = f" with {ui_inputs['service_name']} service" if ui_inputs["service_name"] else ""
        st.info(f"Using model: {model_name}{service_info}")
            
        with st.spinner("Mixing…"):
            transcript, score_a, score_b = run_date(
                ui_inputs["profile_a"], 
                ui_inputs["profile_b"],
                ui_inputs["name_a"],
                ui_inputs["name_b"],
                ui_inputs["rounds"], 
                model_name,
                ui_inputs["theme"],
                ui_inputs["service_name"]
            )
        
        # Display the results
        display_results(transcript, score_a, score_b, ui_inputs["name_a"], ui_inputs["name_b"], model_name)
    except Exception as e:
        error_message = str(e)
        st.error(f"An error occurred: {error_message}")
        st.info("Try using a different model (like gpt-4o) or refreshing the page.")
