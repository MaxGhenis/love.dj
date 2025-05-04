#!/usr/bin/env python3
"""
Test script to simulate EDSL Model.check_working_models().

This script creates a mock of the EDSL Model class that returns
a realistic set of models similar to what the real EDSL would return.
"""
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Create a mock for the EDSL Model class
class MockModel:
    @staticmethod
    def check_working_models():
        """Simulate what the real EDSL would return."""
        logger.info("Mock EDSL returning simulated models...")
        
        # This is what EDSL would typically return - a dictionary of providers to lists of models
        return {
            "openai": [
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "gpt-4-vision-preview",
                "gpt-4-0125-preview",
                "gpt-4-1106-preview",
                "gpt-4-0613",
                "gpt-4",
                "gpt-3.5-turbo-1106"
            ],
            "anthropic": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
                "claude-2.1",
                "claude-2.0",
                "claude-instant-1.2"
            ],
            "google": [
                "gemini-1.5-pro",
                "gemini-1.5-flash",
                "gemini-1.0-pro",
                "gemini-1.0-pro-vision"
            ],
            "mistral": [
                "mistral-large-latest",
                "mistral-medium-latest",
                "mistral-small-latest"
            ],
            "groq": [
                "llama-2-70b-chat",
                "llama-3-70b-8192",
                "llama-3-8b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it"
            ]
        }

# Modify sys.modules to inject our mock
sys.modules['edsl'] = type('edsl', (), {'Model': MockModel})

# Now import our models utility to test it with the mock
try:
    from src.utils.models import get_all_models, format_models_for_selectbox
    
    # Get all the models as a flat list
    all_models = get_all_models()
    print(f"\nFound {len(all_models)} models from mock EDSL")
    
    # Get the models formatted for the selectbox
    formatted_models = format_models_for_selectbox()
    print(f"Formatted {len(formatted_models)} models for the selectbox")
    
    # Show the models
    print("\nFirst 10 models in the selectbox:")
    for i, model in enumerate(formatted_models[:10]):
        print(f"{i+1}. {model}")
    
    # Now simulate what the Streamlit app would do
    print("\nSimulating Streamlit selectbox:")
    
    # Find the default model index
    default_model_index = 0
    for i, model in enumerate(formatted_models):
        if model == "gpt-4o":
            default_model_index = i
            break
            
    print(f"Default model index: {default_model_index}")
    print(f"Default model: {formatted_models[default_model_index]}")
    
    # Check that we have a good number of models
    if len(formatted_models) < 10:
        print("\n⚠️ WARNING: Very few models found, the dropdown would be almost empty!")
    else:
        print(f"\n✅ PASS: Dropdown would show {len(formatted_models)} models")
        
except ImportError as e:
    print(f"Error importing model utils: {e}")
except Exception as e:
    print(f"Error in model utils: {e}")