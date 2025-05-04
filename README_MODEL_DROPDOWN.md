# Model Dropdown Implementation

This document explains how the model dropdown in the Streamlit app works with EDSL's `Model.check_working_models()`.

## Overview

The model dropdown shows all available models from EDSL without any filtering or categorization. This is implemented in:

- `src/utils/models.py`: Contains the functions to get and format models
- `src/ui/streamlit_app.py`: Displays the models in a dropdown

## How It Works

1. When the Streamlit app starts, it calls `format_models_for_selectbox()` to get a list of all available models
2. This function calls `get_all_models()`, which directly uses EDSL's `Model.check_working_models()`
3. The models are extracted from EDSL's response, sorted alphabetically, and displayed in the dropdown
4. The dropdown is a simple Streamlit selectbox with no categorization or filtering

## Implementation Details

Our implementation handles both formats that EDSL's `Model.check_working_models()` might return:

1. A dictionary mapping provider names to lists of models (older EDSL versions)
   ```python
   {
     "openai": ["gpt-4o", "gpt-4-turbo", ...],
     "anthropic": ["claude-3-opus-20240229", ...],
     ...
   }
   ```

2. A list of lists where each inner list contains provider and model name (newer EDSL versions)
   ```python
   [
     ["openai", "gpt-4o", ...],
     ["anthropic", "claude-3-opus-20240229", ...],
     ...
   ]
   ```

The implementation extracts model names, removes duplicates, sorts them alphabetically, and ensures the default model (`gpt-4o`) is always included.

## Debugging

If you're seeing only `gpt-4o` in the dropdown:

1. Check if EDSL is properly installed: `pip install edsl`
2. Verify your EDSL API credentials and configuration
3. Run `python debug_models.py` to see what models EDSL is returning
4. Check `edsl_models.log` for detailed logs about model loading

You can also use our `simulate_edsl.py` script to see what would happen if EDSL returns a realistic set of models.

## Testing

The implementation is tested in `tests/test_models.py`, which verifies:

1. That EDSL's `Model.check_working_models()` returns models in the expected format
2. That our `get_all_models()` function correctly extracts model names
3. That our `format_models_for_selectbox()` function formats them for the Streamlit dropdown

The tests handle both EDSL formats and ensure the code works correctly in all cases.