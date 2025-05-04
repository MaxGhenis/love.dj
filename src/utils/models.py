# src/utils/models.py
import os
import inspect
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('edsl_models.log')
    ]
)
logger = logging.getLogger('edsl_models')

# Save the current file's path for debugging
current_file = os.path.abspath(inspect.getframeinfo(inspect.currentframe()).filename)
logger.info(f"Loading models utility from: {current_file}")

try:
    from edsl import Model
    logger.info("Successfully imported EDSL")
except ImportError as e:
    logger.error(f"Failed to import EDSL: {e}")
    # We don't define a placeholder here because the main app depends on EDSL anyway

def get_all_models():
    """Get all models directly from EDSL using Model.check_working_models().
    
    Returns:
        list: Flat list of all available models
    """
    logger.info("Calling get_all_models()")
    try:
        # Get all models from EDSL's check_working_models
        # This returns a dictionary where keys are providers and values are lists of models
        logger.info("Calling Model.check_working_models()")
        models_by_provider = Model.check_working_models()
        
        if not isinstance(models_by_provider, dict):
            logger.error(f"Unexpected return type from Model.check_working_models(): {type(models_by_provider)}")
            logger.error(f"Value: {models_by_provider}")
            return ["gpt-4o"]
        
        # Log what we received
        logger.info(f"Got response from check_working_models: {len(models_by_provider)} providers")
        for provider, models in models_by_provider.items():
            model_count = len(models) if isinstance(models, list) else 0
            logger.info(f"Provider '{provider}': {model_count} models")
            if model_count > 0 and isinstance(models, list):
                sample = models[:3] if len(models) > 3 else models
                logger.info(f"  Sample: {sample}")
        
        # Flatten the dictionary into a single list of models
        all_models = []
        for provider, provider_models in models_by_provider.items():
            # Skip if provider_models is not a list
            if not isinstance(provider_models, list):
                logger.warning(f"Provider '{provider}' has non-list value: {type(provider_models)}")
                continue
                
            # Add all models from this provider
            all_models.extend(provider_models)
        
        # Remove any duplicates and sort alphabetically
        all_models = sorted(set(all_models))
        
        # If no models were found, fall back to default
        if not all_models:
            logger.warning("No models found in check_working_models, using fallback")
            return ["gpt-4o"]
            
        # Log success
        model_count = len(all_models)
        logger.info(f"Found {model_count} unique models from EDSL")
        
        # If very few models found, that's suspicious 
        if model_count < 10:
            logger.warning(f"WARNING: Only found {model_count} models - suspiciously low!")
            logger.warning(f"Models: {all_models}")
        
        return all_models
    except Exception as e:
        logger.error(f"Error getting working models from EDSL: {e}", exc_info=True)
        # Return a minimal fallback list with just the default model
        return ["gpt-4o"]

def format_models_for_selectbox():
    """Format models for a Streamlit selectbox.
    
    Returns:
        list: List of model names for the selectbox
    """
    logger.info("Calling format_models_for_selectbox()")
    
    # Get all models directly from EDSL
    all_models = get_all_models()
    
    # Ensure gpt-4o is included as the default option
    if "gpt-4o" not in all_models:
        logger.info("Adding gpt-4o as it wasn't found in models list")
        all_models.insert(0, "gpt-4o")
    
    # Log the final list
    logger.info(f"Returning {len(all_models)} models for selectbox")
    if len(all_models) <= 5:
        logger.info(f"All models: {all_models}")
    else:
        logger.info(f"First 5 models: {all_models[:5]}...")
    
    return all_models

# Try to call it once at module import time to help with debugging
logger.info("Testing model utilities during module import")
try:
    models = get_all_models()
    logger.info(f"Initial model check returned {len(models)} models")
except Exception as e:
    logger.error(f"Failed initial model check: {e}", exc_info=True)