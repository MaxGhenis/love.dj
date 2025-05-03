# app.py
import streamlit as st
from src.ui.streamlit_app import (
    setup_ui,
    display_results,
    setup_api_keys,
    create_real_time_transcript_container,
    update_transcript,
)
from src.models.simulation import run_date
from edsl import Config

Config.remote_inference.default = True

# Set up API keys from Streamlit secrets
setup_api_keys()

# Set up the UI
ui_inputs = setup_ui()

# Create a placeholder for the transcript that will be updated in real-time
transcript_container = None
message_placeholders = None
transcript_messages = None

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
        service_info = (
            f" with {ui_inputs['service_name']} service"
            if ui_inputs["service_name"]
            else ""
        )

        # Create the transcript container before starting the simulation
        transcript_container, message_placeholders, transcript_messages = (
            create_real_time_transcript_container()
        )

        # Create a placeholder for typing indicator
        typing_indicator = st.empty()

        # Define callback for real-time updates
        def update_callback(speaker, message):
            # Clear the typing indicator
            typing_indicator.empty()

            # Update the transcript
            update_transcript(
                transcript_container,
                message_placeholders,
                transcript_messages,
                speaker,
                message,
                ui_inputs["gender_a"],
                ui_inputs["gender_b"],
            )

            # Determine who's speaking next (for typing indicator)
            next_speaker = (
                ui_inputs["name_b"]
                if speaker == ui_inputs["name_a"] or speaker == "A"
                else ui_inputs["name_a"]
            )
            if not next_speaker:
                next_speaker = "B" if speaker == "A" else "A"

            # After a brief delay, show next speaker is thinking with animated dots
            import time

            time.sleep(0.2)

            # Show typing indicator for the next speaker
            typing_html = f"""
            <div style="padding: 0.5rem; margin-bottom: 1rem; display: flex; align-items: center;">
                <span style="font-weight: 500; margin-right: 5px;">{next_speaker} is thinking</span>
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
            """
            typing_indicator.markdown(typing_html, unsafe_allow_html=True)

            # Force a small delay to let the UI update
            st.empty()

        # Start the conversation with "Mixing..." message
        mixing_placeholder = st.empty()
        mixing_placeholder.info("Mixing... The conversation will appear below.")

        # For a truly step-by-step approach, we'll use the component functions directly

        # Initialize the date
        from src.models.simulation import (
            initialize_date,
            get_opening_message,
            get_next_response,
            get_date_ratings,
        )

        # Initialize agents and variables
        agent_a, agent_b, display_a, display_b = initialize_date(
            ui_inputs["profile_a"],
            ui_inputs["profile_b"],
            ui_inputs["name_a"],
            ui_inputs["name_b"],
            model_name,
            ui_inputs["theme"],
            ui_inputs["service_name"],
            ui_inputs["gender_a"],
            ui_inputs["gender_b"],
        )

        transcript = []

        # Get the opening message with a slight delay
        opener_entry, history_txt = get_opening_message(
            agent_a, display_a, model_name, ui_inputs["service_name"]
        )
        transcript.append(opener_entry)
        update_callback(opener_entry[0], opener_entry[1])

        # Add a small delay between messages
        import time

        time.sleep(0.5)

        # Process each round of conversation with delays between messages
        for turn in range(ui_inputs["rounds"]):
            # B's response
            b_entry, history_txt = get_next_response(
                agent_b,
                agent_a,
                display_b,
                turn,
                "B",
                history_txt,
                model_name,
                ui_inputs["service_name"],
            )
            transcript.append(b_entry)
            update_callback(b_entry[0], b_entry[1])
            time.sleep(0.5)  # Add a short delay

            # A's response
            a_entry, history_txt = get_next_response(
                agent_a,
                agent_b,
                display_a,
                turn,
                "A",
                history_txt,
                model_name,
                ui_inputs["service_name"],
            )
            transcript.append(a_entry)

            # If this is the last message, don't show next typing indicator
            if turn == ui_inputs["rounds"] - 1:
                # Clear typing indicator
                typing_indicator.empty()
                # Update without showing typing for next person
                update_transcript(
                    transcript_container,
                    message_placeholders,
                    transcript_messages,
                    a_entry[0],
                    a_entry[1],
                    ui_inputs["gender_a"],
                    ui_inputs["gender_b"],
                )
                time.sleep(0.5)
                # Show a rating calculation message
                typing_indicator.markdown(
                    """
                <div style="padding: 0.5rem; margin-bottom: 1rem; display: flex; align-items: center;">
                    <span style="font-weight: 500; margin-right: 5px;">Calculating ratings</span>
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                # Normal update with typing indicator for next person
                update_callback(a_entry[0], a_entry[1])
                time.sleep(0.5)  # Add a short delay

        # Get ratings
        score_a, score_b = get_date_ratings(
            agent_a, agent_b, history_txt, model_name, ui_inputs["service_name"]
        )

        # Clear the "Mixing..." message and typing indicator
        mixing_placeholder.empty()
        typing_indicator.empty()

        # Display the final results (ratings)
        display_results(
            transcript,
            score_a,
            score_b,
            ui_inputs["name_a"],
            ui_inputs["name_b"],
            model_name,
            transcript_container,
            message_placeholders,
            transcript_messages,
        )
    except Exception as e:
        error_message = str(e)
        st.error(f"An error occurred: {error_message}")
        st.info("Try using a different model (like gpt-4o) or refreshing the page.")
