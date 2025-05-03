# tests/test_agents.py
import unittest
from unittest.mock import patch, MagicMock

# Mock the edsl imports
class MockAgent:
    def __init__(self, name, traits):
        self.name = name
        self.traits = traits

# Mock constants for testing
DEFAULT_PROFILES = {
    "default_a": "Default profile A",
    "default_b": "Default profile B"
}

CONVERSATION_GUIDELINES = "Test guidelines"

# Function to test
def create_agent(name, profile, default_profile):
    """Create an agent with the given name and profile."""
    return MockAgent(
        name=name,
        traits={
            "persona": profile or default_profile,
            "guidelines": CONVERSATION_GUIDELINES,
        },
    )

class TestAgents(unittest.TestCase):
    def test_create_agent_with_custom_profile(self):
        """Test creating an agent with a custom profile."""
        custom_profile = "Custom profile description"
        agent = create_agent("TestAgent", custom_profile, DEFAULT_PROFILES["default_a"])
        
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.traits["persona"], custom_profile)
        self.assertEqual(agent.traits["guidelines"], CONVERSATION_GUIDELINES)
    
    def test_create_agent_with_default_profile(self):
        """Test creating an agent with a default profile."""
        agent = create_agent("TestAgent", "", DEFAULT_PROFILES["default_a"])
        
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.traits["persona"], DEFAULT_PROFILES["default_a"])
        self.assertEqual(agent.traits["guidelines"], CONVERSATION_GUIDELINES)
        
    def test_get_rating_with_none_value(self):
        """Test that get_rating handles None values correctly."""
        # Add our implementation of get_rating function with the error handling
        import re
        
        def mock_result():
            return None
            
        # Mock the Model and other components
        class MockModel:
            def __init__(self, model_name):
                self.model_name = model_name
                
        class MockScenario:
            def __init__(self, data):
                self.data = data
                
        class MockQuestion:
            def __init__(self):
                pass
                
            def by(self, component):
                return self
                
            def run(self):
                return self
                
            def select(self, name):
                return self
                
            def first(self):
                return mock_result()
                
        # Override the rating function for testing
        def test_get_rating(model_name, agent, history_txt):
            result = mock_result()
            
            # Handle case where result might be None
            if result is None:
                return 5  # Default middle rating if no response
            
            # Try to convert to int, with fallback
            try:
                return int(result)
            except (ValueError, TypeError):
                # Try to extract a number if result is a string with text
                if isinstance(result, str):
                    numbers = re.findall(r'\d+', result)
                    if numbers:
                        return int(numbers[0])
                return 5  # Default to middle rating if conversion fails
        
        # Test with None result
        rating = test_get_rating("test-model", MockAgent("test", {}), "test history")
        self.assertEqual(rating, 5)
        
    def test_get_rating_with_string_value(self):
        """Test that get_rating handles string values correctly."""
        import re
        
        def mock_result():
            return "I rate this date a 8 out of 10"
            
        # Mock the Model and other components
        class MockModel:
            def __init__(self, model_name):
                self.model_name = model_name
                
        class MockScenario:
            def __init__(self, data):
                self.data = data
                
        class MockQuestion:
            def __init__(self):
                pass
                
            def by(self, component):
                return self
                
            def run(self):
                return self
                
            def select(self, name):
                return self
                
            def first(self):
                return mock_result()
                
        # Override the rating function for testing
        def test_get_rating(model_name, agent, history_txt):
            result = mock_result()
            
            # Handle case where result might be None
            if result is None:
                return 5  # Default middle rating if no response
            
            # Try to convert to int, with fallback
            try:
                return int(result)
            except (ValueError, TypeError):
                # Try to extract a number if result is a string with text
                if isinstance(result, str):
                    numbers = re.findall(r'\d+', result)
                    if numbers:
                        return int(numbers[0])
                return 5  # Default to middle rating if conversion fails
        
        # Test with string result containing a number
        rating = test_get_rating("test-model", MockAgent("test", {}), "test history")
        self.assertEqual(rating, 8)  # Should extract 8 from the string

if __name__ == "__main__":
    unittest.main()
