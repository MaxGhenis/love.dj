# src/ui/streamlit_app.py
import streamlit as st
import os
from src.models.simulation import run_date
from src.utils.models import format_models_for_selectbox
from src.utils.models import DEFAULT_MODEL_LABEL


def setup_ui():
    """Set up the Streamlit UI."""
    st.set_page_config(page_title="🎧 love.dj", page_icon="🎧")
    st.title("🎧 love.dj")

    col1, col2 = st.columns(2)
    with col1:
        name_a = st.text_input("Person A's name", value="")

        # Gender selection for person A
        gender_a = st.selectbox(
            "Person A's gender",
            options=["he/him", "she/her", "they/them"],
            index=0,
            help="This affects pronouns and emoji representation",
        )

        profile_a = st.text_area(
            "Profile A (who is *this* person?)",
            height=150,
            placeholder="e.g. 28 y/o product-manager, loves jazz & climbing…",
        )
    with col2:
        name_b = st.text_input("Person B's name", value="")

        # Gender selection for person B
        gender_b = st.selectbox(
            "Person B's gender",
            options=["he/him", "she/her", "they/them"],
            index=1,  # Default to she/her for person B
            help="This affects pronouns and emoji representation",
        )

        profile_b = st.text_area(
            "Profile B (and their date?)",
            height=150,
            placeholder="e.g. 30 y/o PhD student, avid reader, vegan…",
        )

    # Additional options
    st.subheader("Date Settings")
    col3, col4 = st.columns(2)
    with col3:
        rounds = st.slider("How many back-and-forths?", 1, 6, value=3)

        # Get models for the dropdown directly from EDSL
        all_models = format_models_for_selectbox()

        # Find the index of the default model (gpt-4o)
        default_model_index = 0
        for i, model in enumerate(all_models):
            if model == "gpt-4o":
                default_model_index = i
                break

        # Add help text for the model selector
        model_help = """
        Select a language model to use for the date simulation.
        
        These models are retrieved directly from EDSL's available models.
        """

        # Create a simple selectbox for model selection
        default_ix = (
            all_models.index(DEFAULT_MODEL_LABEL)
            if DEFAULT_MODEL_LABEL in all_models
            else 0
        )
        model_name = st.selectbox(
            "Language Model",
            options=all_models,
            index=default_ix,
            help=model_help,
        )

        # Service name is always auto-detected
        service_name = "None (auto)"
    with col4:
        theme = st.text_input(
            "Date location/theme (optional)",
            value="",
            placeholder="e.g. a coffee shop, hiking trail, fancy restaurant...",
        )

    go = st.button("🚀 Spin the decks")

    # Add footer with EDSL info
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; font-size: 0.8em; color: #888;">
        Powered by <a href="https://www.expectedparrot.com/" target="_blank">EDSL</a> • 
        <a href="https://www.expectedparrot.com/models" target="_blank">Supported Models</a> •
        <a href="https://github.com/expectedparrot/edsl" target="_blank">GitHub</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return {
        "name_a": name_a,
        "profile_a": profile_a,
        "gender_a": gender_a,
        "name_b": name_b,
        "profile_b": profile_b,
        "gender_b": gender_b,
        "rounds": rounds,
        "model_name": model_name,
        "service_name": None,  # Always use auto-detection
        "theme": theme,
        "go": go,
    }


def create_real_time_transcript_container():
    """Create a container for real-time transcript display.

    Returns:
        tuple: (transcript_container, message_placeholders, transcript_messages)
              where message_placeholders is for real-time updates and
              transcript_messages keeps track of all messages
    """
    st.subheader("💬 Transcript")

    # Add some CSS to style the transcript container
    st.markdown(
        """
    <style>
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user-a {
        background-color: rgba(240, 242, 246, 0.5);
        border-left: 5px solid #9AD1F5;
    }
    .chat-message.user-b {
        background-color: rgba(240, 242, 246, 0.5);
        border-left: 5px solid #F5C3A9;
    }
    .chat-message .avatar {
        font-size: 1.25rem;
        width: 2.5rem;
        height: 1.5rem;
        text-align: center;
        float: left;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex-grow: 1;
    }
    .chat-message .name {
        font-weight: bold;
        font-size: 0.9rem;
        color: #424242;
    }
    .typing-indicator {
        display: inline-block;
        margin-left: 5px;
    }
    .typing-indicator span {
        display: inline-block;
        background-color: #808080;
        width: 5px;
        height: 5px;
        border-radius: 50%;
        margin: 0 1px;
        animation: typing 1.5s infinite ease-in-out;
    }
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
        }
        30% {
            transform: translateY(-5px);
        }
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Create a container with a bordered style
    transcript_container = st.container()
    # List to store message placeholders for real-time updates
    message_placeholders = []
    # List to track all transcript messages
    transcript_messages = []

    return transcript_container, message_placeholders, transcript_messages


def update_transcript(
    transcript_container,
    message_placeholders,
    transcript_messages,
    speaker,
    message,
    gender_a="he/him",
    gender_b="she/her",
):
    """Add a new message to the transcript in real-time.

    Args:
        transcript_container: The container to display messages in
        message_placeholders: List of message placeholders
        transcript_messages: List of all transcript messages
        speaker: The name of the speaker
        message: The message content
        gender_a: Gender/pronouns of person A
        gender_b: Gender/pronouns of person B
    """
    with transcript_container:
        # Create a new placeholder for this message if needed
        if len(message_placeholders) <= len(transcript_messages):
            placeholder = st.empty()
            message_placeholders.append(placeholder)
        else:
            placeholder = message_placeholders[len(transcript_messages)]

        # Determine which user class to use (for styling)
        if not transcript_messages:
            # This is the first message
            user_class = "user-a"
        else:
            user_class = (
                "user-a"
                if speaker.lower() == "a"
                or speaker.lower() == transcript_messages[0][0].lower()
                else "user-b"
            )

        # Get appropriate emoji based on gender
        gender = gender_a if user_class == "user-a" else gender_b

        if gender == "he/him":
            emoji = "👨"
        elif gender == "she/her":
            emoji = "👩"
        else:  # they/them
            emoji = "🧑"

        # Format message with HTML for styling
        html_message = f"""
        <div class="chat-message {user_class}">
            <div class="avatar">
                {emoji}
            </div>
            <div class="message">
                <div class="name">{speaker}</div>
                {message}
            </div>
        </div>
        """

        # Display the message with custom HTML
        placeholder.markdown(html_message, unsafe_allow_html=True)

        # Add to our transcript list
        transcript_messages.append((speaker, message))


def display_results(
    transcript,
    score_a,
    score_b,
    name_a,
    name_b,
    model_name="",
    transcript_container=None,
    message_placeholders=None,
    transcript_messages=None,
):
    """Display the results of the date simulation."""
    if model_name:
        st.success(f"Date simulated with model: {model_name}")

    # Display ratings if we have them
    if score_a is not None and score_b is not None:
        st.subheader("⭐ Ratings")

        # Use the provided names or default to A/B
        display_a = name_a if name_a else "A"
        display_b = name_b if name_b else "B"

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{display_a}'s score", f"{score_a}/10")
        with col2:
            st.metric(f"{display_b}'s score", f"{score_b}/10")
        with col3:
            st.metric("Average", f"{(score_a+score_b)/2:.1f}/10")

        st.caption(
            "Powered by EDSL – agents, scenarios & questions handle the heavy lifting of multi-agent dialogue"
        )
