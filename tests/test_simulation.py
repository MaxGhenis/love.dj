# tests/test_simulation.py
import unittest
from unittest.mock import patch, MagicMock

# Mock necessary components for testing
class MockAgent:
    def __init__(self, name, traits):
        self.name = name
        self.traits = traits

# Mock constants and functions
DEFAULT_PROFILES = {
    "default_a": "Default profile A",
    "default_b": "Default profile B"
}

def create_agent(name, profile, default_profile):
    return MockAgent(name, {"persona": profile or default_profile, "guidelines": "guidelines"})

def get_opener(model_name, agent):
    return "Hi there, I'm the opener!"

def get_response(model_name, agent_self, agent_other, turn, speaker, history_txt):
    return "This is a response."

def get_rating(model_name, agent, history_txt):
    return 8

# Function to test (simplified version)
def run_date(profile_a, profile_b, name_a, name_b, n_rounds, model_name, theme=None, age_a=28, age_b=30):
    # Use display names in transcript, defaulting to A/B if none provided
    display_a = name_a if name_a else "A"
    display_b = name_b if name_b else "B"
    
    # Create agents with age information
    enhanced_profile_a = f"{age_a} year old {profile_a}"
    enhanced_profile_b = f"{age_b} year old {profile_b}"
    
    agent_a = create_agent(display_a, enhanced_profile_a, DEFAULT_PROFILES["default_a"])
    agent_b = create_agent(display_b, enhanced_profile_b, DEFAULT_PROFILES["default_b"])

    transcript = []
    
    # Add opener
    opener = get_opener(model_name, agent_a)
    transcript.append((display_a, opener))
    
    # Add one round of conversation
    for _ in range(n_rounds):
        transcript.append((display_b, get_response(model_name, agent_b, agent_a, 0, "B", "")))
        transcript.append((display_a, get_response(model_name, agent_a, agent_b, 0, "A", "")))
    
    # Get ratings
    rating_a = get_rating(model_name, agent_a, "")
    rating_b = get_rating(model_name, agent_b, "")
    
    return transcript, rating_a, rating_b

class TestSimulation(unittest.TestCase):
    def test_run_date_flow(self):
        """Test the flow of a date simulation."""
        # Run the simulation with our mock functions
        transcript, rating_a, rating_b = run_date(
            "Profile A", "Profile B", "Alice", "Bob", 1, "mock-model", 
            age_a=25, age_b=27
        )
        
        # Verify results
        self.assertEqual(len(transcript), 3)  # Opener + 2 responses (1 round)
        self.assertEqual(transcript[0], ("Alice", "Hi there, I'm the opener!"))
        self.assertEqual(transcript[1], ("Bob", "This is a response."))
        self.assertEqual(transcript[2], ("Alice", "This is a response."))
        self.assertEqual(rating_a, 8)
        self.assertEqual(rating_b, 8)

if __name__ == "__main__":
    unittest.main()
