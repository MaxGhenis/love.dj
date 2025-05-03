# src/ui/streamlit_app.py
import streamlit as st
import os
from src.models.simulation import run_date

def setup_api_keys():
    """Set up API keys from Streamlit secrets or environment variables.
    
    This function checks for API keys in Streamlit secrets and sets them
    as environment variables for EDSL to use.
    """
    # Set up API keys from secrets
    if hasattr(st, 'secrets') and 'edsl' in st.secrets:
        edsl_secrets = st.secrets.edsl
        
        # Set EDSL key if available
        if 'api_key' in edsl_secrets:
            os.environ['EDSL_API_KEY'] = edsl_secrets.api_key
            
        # Set provider-specific keys if available in secrets
        providers = [
            'openai', 'anthropic', 'google', 'mistral', 
            'together', 'groq', 'azure', 'bedrock'
        ]
        
        for provider in providers:
            if provider in edsl_secrets:
                if 'api_key' in edsl_secrets[provider]:
                    os.environ[f'{provider.upper()}_API_KEY'] = edsl_secrets[provider].api_key
    
    # Check for the keys we need
    if 'EDSL_API_KEY' not in os.environ:
        st.warning(
            "⚠️ EDSL API key not found in secrets. "
            "You may encounter issues with model services. "
            "For Streamlit Community Cloud, please set up your secrets.toml file."
        )

def setup_ui():
    """Set up the Streamlit UI."""
    st.set_page_config(page_title="🎧 love.dj", page_icon="🎧")
    st.title("🎧 love.dj")
    
    col1, col2 = st.columns(2)
    with col1:
        name_a = st.text_input("Person A's name", value="")
        profile_a = st.text_area(
            "Profile A (who is *this* person?)",
            height=180,
            placeholder="e.g. 28 y/o product-manager, loves jazz & climbing…",
        )
    with col2:
        name_b = st.text_input("Person B's name", value="")
        profile_b = st.text_area(
            "Profile B (and their date?)",
            height=180,
            placeholder="e.g. 30 y/o PhD student, avid reader, vegan…",
        )

    # Additional options
    st.subheader("Date Settings")
    col3, col4 = st.columns(2)
    with col3:
        rounds = st.slider("How many back-and-forths?", 1, 6, value=3)
        
        # Split into two columns for model name and service provider
        model_col1, model_col2 = st.columns([3, 2])
        
        with model_col1:
            model_name = st.text_input(
                "Model name", 
                value="gpt-4o",
                help="Enter any model name that EDSL supports (e.g., gpt-4o, claude-3-opus-20240229, gemini-1.5-pro)"
            )
            
        with model_col2:
            service_providers = [
                "None (auto)",
                "anthropic",
                "azure",
                "bedrock",
                "deep_infra",
                "deepseek",
                "google",
                "groq",
                "mistral",
                "ollama",
                "openai",
                "perplexity",
                "together"
            ]
            service_name = st.selectbox(
                "Service provider",
                options=service_providers,
                index=0,
                help="Select the service provider for this model"
            )
    with col4:
        theme = st.text_input(
            "Date location/theme (optional)", 
            value="", 
            placeholder="e.g. a coffee shop, hiking trail, fancy restaurant..."
        )
        
    go = st.button("🚀 Spin the decks")
    
    return {
        "name_a": name_a,
        "profile_a": profile_a,
        "name_b": name_b,
        "profile_b": profile_b,
        "rounds": rounds,
        "model_name": model_name,
        "service_name": None if service_name == "None (auto)" else service_name,
        "theme": theme,
        "go": go
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
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    # Create a container with a bordered style
    transcript_container = st.container()
    # List to store message placeholders for real-time updates
    message_placeholders = []
    # List to track all transcript messages
    transcript_messages = []
    
    return transcript_container, message_placeholders, transcript_messages


def update_transcript(transcript_container, message_placeholders, transcript_messages, speaker, message):
    """Add a new message to the transcript in real-time.
    
    Args:
        transcript_container: The container to display messages in
        message_placeholders: List of message placeholders
        transcript_messages: List of all transcript messages
        speaker: The name of the speaker
        message: The message content
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
            user_class = "user-a" if speaker.lower() == "a" or speaker.lower() == transcript_messages[0][0].lower() else "user-b"
        
        # Format message with HTML for styling
        html_message = f"""
        <div class="chat-message {user_class}">
            <div class="avatar">
                {'🧑' if user_class == 'user-a' else '👩‍💼'}
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


def display_results(transcript, score_a, score_b, name_a, name_b, model_name="", 
                   transcript_container=None, message_placeholders=None, transcript_messages=None):
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
