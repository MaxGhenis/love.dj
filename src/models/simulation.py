# src/models/simulation.py
from src.models.agents import (
    create_agent,
    get_opener,
    get_response,
    get_rating,
    DEFAULT_PROFILES,
)

def initialize_date(profile_a, profile_b, name_a, name_b, model_name, theme=None, service_name=None):
    """Initialize a date simulation and create the agents.
    
    Args:
        profile_a: Description of person A
        profile_b: Description of person B
        name_a: Name of person A
        name_b: Name of person B
        model_name: Name of the LLM to use
        theme: Optional theme/location for the date
        service_name: Optional service provider name
        
    Returns:
        tuple: (agent_a, agent_b, display_a, display_b)
    """
    # Use display names in transcript, defaulting to A/B if none provided
    display_a = name_a if name_a else "A"
    display_b = name_b if name_b else "B"
    
    # Create agents
    agent_a = create_agent(display_a, profile_a, DEFAULT_PROFILES["default_a"])
    agent_b = create_agent(display_b, profile_b, DEFAULT_PROFILES["default_b"])
    
    # Keep track of the model being used
    print(f"Using model in simulation: {model_name}")
    if service_name:
        print(f"Using service provider: {service_name}")
    
    # Add theme/location context if provided
    if theme:
        theme_intro = f"You are on a date at {theme}. "
        agent_a.traits["guidelines"] = theme_intro + agent_a.traits["guidelines"]
        agent_b.traits["guidelines"] = theme_intro + agent_b.traits["guidelines"]
    
    return agent_a, agent_b, display_a, display_b


def get_opening_message(agent_a, display_a, model_name, service_name=None):
    """Get the opening message for the conversation.
    
    Args:
        agent_a: The agent who starts the conversation
        display_a: Display name for agent A
        model_name: Name of the LLM to use
        service_name: Optional service provider name
        
    Returns:
        tuple: (transcript entry, history text)
    """
    # Seed opener from A to start the conversation
    opener = get_opener(model_name, agent_a, service_name)
    transcript_entry = (display_a, opener)
    history_txt = f"{display_a}: {opener}\n"
    
    return transcript_entry, history_txt


def get_next_response(agent_self, agent_other, display, turn, speaker, history_txt, model_name, service_name=None):
    """Get the next response in the conversation.
    
    Args:
        agent_self: The agent responding
        agent_other: The other agent
        display: Display name for the responding agent
        turn: The current turn number
        speaker: The speaker identifier (A or B)
        history_txt: The conversation history so far
        model_name: Name of the LLM to use
        service_name: Optional service provider name
        
    Returns:
        tuple: (transcript entry, updated history)
    """
    answer = get_response(
        model_name, 
        agent_self, 
        agent_other, 
        turn, 
        speaker, 
        history_txt,
        service_name
    )
    
    transcript_entry = (display, answer)
    updated_history = history_txt + f"{display}: {answer}\n"
    
    return transcript_entry, updated_history


def get_date_ratings(agent_a, agent_b, history_txt, model_name, service_name=None):
    """Get ratings from both participants after the date.
    
    Args:
        agent_a: Agent A
        agent_b: Agent B
        history_txt: The complete conversation history
        model_name: Name of the LLM to use
        service_name: Optional service provider name
        
    Returns:
        tuple: (rating_a, rating_b)
    """
    rating_a = get_rating(model_name, agent_a, history_txt, service_name)
    rating_b = get_rating(model_name, agent_b, history_txt, service_name)
    
    return rating_a, rating_b


def run_date(profile_a, profile_b, name_a, name_b, n_rounds, model_name, theme=None, service_name=None, callback=None):
    """Simulate a date, return transcript and ratings.
    
    This version uses the individual date steps to simulate the date and support callbacks.
    
    Args:
        profile_a: Description of person A
        profile_b: Description of person B
        name_a: Name of person A
        name_b: Name of person B
        n_rounds: Number of back-and-forth exchanges
        model_name: Name of the LLM to use
        theme: Optional theme/location for the date
        service_name: Optional service provider name
        callback: Optional callback function to call after each message
        
    Returns:
        tuple: (transcript, rating_a, rating_b)
    """
    # Initialize the date
    agent_a, agent_b, display_a, display_b = initialize_date(
        profile_a, profile_b, name_a, name_b, model_name, theme, service_name
    )
    
    transcript = []  # list[(speaker, text)]
    
    # Get the opening message
    opener_entry, history_txt = get_opening_message(agent_a, display_a, model_name, service_name)
    transcript.append(opener_entry)
    
    # Call the callback with the opener message
    if callback:
        callback(opener_entry[0], opener_entry[1])
    
    # ---------- conversation loop ----------
    for turn in range(n_rounds):
        # B's response
        b_entry, history_txt = get_next_response(
            agent_b, agent_a, display_b, turn, "B", history_txt, model_name, service_name
        )
        transcript.append(b_entry)
        if callback:
            callback(b_entry[0], b_entry[1])
        
        # A's response
        a_entry, history_txt = get_next_response(
            agent_a, agent_b, display_a, turn, "A", history_txt, model_name, service_name
        )
        transcript.append(a_entry)
        if callback:
            callback(a_entry[0], a_entry[1])
    
    # ---------- each agent rates the date ----------
    rating_a, rating_b = get_date_ratings(agent_a, agent_b, history_txt, model_name, service_name)
    
    return transcript, rating_a, rating_b
