# src/ui/streamlit_app.py
import streamlit as st
from src.models.simulation import run_date

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

def display_results(transcript, score_a, score_b, name_a, name_b, model_name=""):
    """Display the results of the date simulation."""
    if model_name:
        st.success(f"Date simulated with model: {model_name}")
        
    st.subheader("💬 Transcript")
    
    # Create a container with a bordered style
    transcript_container = st.container()
    with transcript_container:
        for speaker, line in transcript:
            # Check if the line already starts with the speaker's name to avoid duplication
            if line.startswith(f"{speaker}:") or line.startswith(f"{speaker},") or line.startswith(f"Hi, I'm {speaker}"):
                st.markdown(f"**{speaker}:** {line}")
            else:
                st.markdown(f"**{speaker}:** {line}")
    
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
