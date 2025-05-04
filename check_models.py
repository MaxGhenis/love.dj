#!/usr/bin/env python3
"""
Debug script for EDSL models.

This script retrieves all available models from EDSL using the same approach
as the main application, and prints them in a readable format for debugging.

Run this script to verify what models EDSL is actually returning.
"""
import json
import logging
from edsl import Model
from src.utils.models import get_all_models, format_models_for_selectbox

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("edsl_models.log"),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

def print_separator(title=None):
    """Print a separator line with optional title."""
    width = 80
    if title:
        logger.info(f"\n{'-' * 10} {title} {'-' * (width - 12 - len(title))}")
    else:
        logger.info(f"\n{'-' * width}")

logger.info("Starting EDSL model check")

# First step: Call EDSL directly
print_separator("Direct EDSL Model.check_working_models() Output")
try:
    # Get the available working models
    logger.info("Calling Model.check_working_models()")
    working_models = Model.check_working_models()
    
    # Print the output to understand its structure
    logger.info(f"Type of working_models: {type(working_models)}")
    
    # If it's a dictionary, print keys and values separately for better readability
    if isinstance(working_models, dict):
        logger.info(f"Keys in working_models: {list(working_models.keys())}")
        
        # For each provider, log how many models are available
        for key, values in working_models.items():
            if isinstance(values, list):
                logger.info(f"Provider '{key}' has {len(values)} models")
                if values:  # If there are models, log a sample
                    logger.info(f"  Sample: {values[:3]}")
            else:
                logger.info(f"Provider '{key}' has unexpected value type: {type(values)}")
    else:
        logger.info(f"working_models is not a dictionary but a {type(working_models)}")
        logger.info(f"Content: {working_models}")
    
    # Write the full output to a file for reference
    with open("edsl_models_output.json", "w") as f:
        json.dump(working_models, f, indent=2)
    logger.info("Wrote raw output to edsl_models_output.json")
        
except Exception as e:
    logger.error(f"Error getting models directly from EDSL: {e}", exc_info=True)

# Second step: Use our utility function
print_separator("Our get_all_models() Output")
try:
    all_models = get_all_models()
    model_count = len(all_models)
    logger.info(f"Total models: {model_count}")
    
    # Check if we have a substantial number of models
    if model_count < 100:
        logger.warning(f"WARNING: Only found {model_count} models. EDSL should return 100+ models!")
    else:
        logger.info(f"SUCCESS: Found {model_count} models (expecting 100+)")
        
    # Show a sample of the models
    logger.info(f"First 20 models: {', '.join(all_models[:20])}{'...' if len(all_models) > 20 else ''}")
    
    # Check for specific models we expect to see
    expected_models = [
        'gpt-4o', 
        'gpt-4-turbo', 
        'gpt-3.5-turbo', 
        'claude-3-opus-20240229',
        'claude-3-sonnet-20240229', 
        'gemini-1.5-pro'
    ]
    
    found_models = [model for model in expected_models if model in all_models]
    missing_models = [model for model in expected_models if model not in all_models]
    
    if found_models:
        logger.info(f"Found expected models: {', '.join(found_models)}")
    
    if missing_models:
        logger.warning(f"WARNING: Could not find some expected models: {', '.join(missing_models)}")
except Exception as e:
    logger.error(f"Error in get_all_models(): {e}", exc_info=True)

# Third step: Format for selectbox
print_separator("Our format_models_for_selectbox() Output")
try:
    formatted_models = format_models_for_selectbox()
    logger.info(f"Total models for dropdown: {len(formatted_models)}")
    logger.info(f"Default model: {formatted_models[0]}")
    logger.info(f"All models: {', '.join(formatted_models[:10])}{'...' if len(formatted_models) > 10 else ''}")
except Exception as e:
    logger.error(f"Error in format_models_for_selectbox(): {e}", exc_info=True)

# Save the processed data
print_separator("Saving Processed Output")
try:
    with open('edsl_processed_models.json', 'w') as f:
        json.dump({
            'all_models': all_models if 'all_models' in locals() else None,
            'formatted_models': formatted_models if 'formatted_models' in locals() else None
        }, f, indent=2)
    logger.info("Saved processed model data to edsl_processed_models.json")
except Exception as e:
    logger.error(f"Error saving processed output: {e}", exc_info=True)

print_separator()
logger.info("Debug complete.")

if 'all_models' in locals() and len(all_models) <= 1:
    logger.warning("CRITICAL ISSUE: Only showing gpt-4o in the dropdown!")
    logger.warning("The dropdown should contain 100+ models from various providers.")
    logger.warning("\nPossible causes:")
    logger.warning("1. EDSL's check_working_models() is not returning models (check edsl_models_output.json)")
    logger.warning("2. Models are not being properly flattened in get_all_models()")
    logger.warning("3. The formatted models are not being passed to the Streamlit selectbox")
else:
    logger.info("If Streamlit is showing all models correctly, you're good to go!")
    logger.info("If not, review the logs above for any warnings or errors")

logger.info("EDSL model check complete")