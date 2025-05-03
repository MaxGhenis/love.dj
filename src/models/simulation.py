# src/models/simulation.py
from src.models.agents import (
    create_agent,
    get_opener,
    get_response,
    get_rating,
    DEFAULT_PROFILES,
)

def run_date(profile_a, profile_b, name_a, name_b, n_rounds, model_name, theme=None):
    """Simulate a date, return transcript and ratings.
    
    Args:
        profile_a: Description of person A
        profile_b: Description of person B
        name_a: Name of person A
        name_b: Name of person B
        n_rounds: Number of back-and-forth exchanges
        model_name: Name of the LLM to use
        theme: Optional theme/location for the date
        
    Returns:
        tuple: (transcript, rating_a, rating_b)
    """
    # Use display names in transcript, defaulting to A/B if none provided
    display_a = name_a if name_a else "A"
    display_b = name_b if name_b else "B"
    
    # Create agents
    agent_a = create_agent(display_a, profile_a, DEFAULT_PROFILES["default_a"])
    agent_b = create_agent(display_b, profile_b, DEFAULT_PROFILES["default_b"])
    
    # Keep track of the model being used
    print(f"Using model in simulation: {model_name}")

    transcript = []  # list[(speaker, text)]
    history_txt = ""
    
    # Add theme/location context if provided
    if theme:
        theme_intro = f"You are on a date at {theme}. "
        agent_a.traits["guidelines"] = theme_intro + agent_a.traits["guidelines"]
        agent_b.traits["guidelines"] = theme_intro + agent_b.traits["guidelines"]
        
    # We don't need to add names to personas since they're already used in the transcript
    # Keep the persona descriptions without adding names to avoid duplication

    # Seed opener from A so the loop is symmetric
    opener = get_opener(model_name, agent_a)
    transcript.append((display_a, opener))
    history_txt += f"{display_a}: {opener}\n"

    # ---------- conversation loop ----------
    for turn in range(n_rounds):
        for speaker, display, agent_self, agent_other in [
            ("B", display_b, agent_b, agent_a),
            ("A", display_a, agent_a, agent_b),
        ]:
            answer = get_response(
                model_name, 
                agent_self, 
                agent_other, 
                turn, 
                speaker, 
                history_txt
            )
            
            transcript.append((display, answer))
            history_txt += f"{display}: {answer}\n"

    # ---------- each agent rates the date ----------
    rating_a = get_rating(model_name, agent_a, history_txt)
    rating_b = get_rating(model_name, agent_b, history_txt)

    return transcript, rating_a, rating_b
