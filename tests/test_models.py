# tests/test_models.py
import unittest
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from edsl import Model
except ImportError:
    print("WARNING: EDSL module not found, skipping EDSL tests")
    Model = None

# Import our models utility
try:
    from src.utils.models import get_all_models, format_models_for_selectbox
except ImportError:
    print("WARNING: Could not import models utilities")
    get_all_models = format_models_for_selectbox = None

class TestModels(unittest.TestCase):
    @unittest.skipIf(Model is None, "EDSL module not available")
    def test_real_models_from_edsl(self):
        """Test retrieving actual models from EDSL - no mocks."""
        # Call the actual EDSL API
        raw_models = Model.check_working_models()
        
        # Verify it returns a list (or dict in older versions)
        self.assertTrue(isinstance(raw_models, list) or isinstance(raw_models, dict), 
                      "EDSL should return a list of model info or dict of providers to models")
        
        # Extract model names
        all_model_names = []
        
        if isinstance(raw_models, list):
            # Handle list format: [[provider, model_name, ...], ...]
            for model_info in raw_models:
                if isinstance(model_info, list) and len(model_info) >= 2:
                    model_name = model_info[1]  # Second item is the model name
                    all_model_names.append(model_name)
        else:
            # Handle dictionary format (for older EDSL versions)
            for provider_models in raw_models.values():
                if isinstance(provider_models, list):
                    all_model_names.extend(provider_models)
                
        # Remove duplicates
        unique_models = set(all_model_names)
        
        # Check we have a substantial number of models
        # (EDSL should provide many models, but we test for at least 10 to be safe)
        self.assertGreaterEqual(len(unique_models), 10, "EDSL should return at least 10 models")
        
        # Check for some common models (at least one of these should exist)
        common_models = ['gpt-4o', 'gpt-4-turbo', 'claude-3-opus-20240229', 'gemini-1.5-pro']
        found_one = any(model in unique_models for model in common_models)
        self.assertTrue(found_one, f"EDSL should return at least one of these models: {common_models}")
    
    @unittest.skipIf(Model is None or get_all_models is None, "EDSL module or models utility not available")
    def test_get_all_models_produces_flat_list(self):
        """Test that our get_all_models function creates a flat list from EDSL data."""
        # Get models directly from EDSL
        raw_models = Model.check_working_models()
        
        # Extract model names to compare
        expected_models = set()
        
        if isinstance(raw_models, list):
            # Handle list format: [[provider, model_name, ...], ...]
            for model_info in raw_models:
                if isinstance(model_info, list) and len(model_info) >= 2:
                    model_name = model_info[1]  # Second item is the model name
                    expected_models.add(model_name)
        else:
            # Handle dictionary format (for older EDSL versions)
            for provider_models in raw_models.values():
                if isinstance(provider_models, list):
                    expected_models.update(provider_models)
        
        # Call our function
        result = get_all_models()
        
        # Check that our function returns a non-empty list of models
        self.assertGreater(len(result), 0, "get_all_models should return at least one model")
        
        # Verify models are alphabetically sorted
        self.assertEqual(result, sorted(result), "Models should be alphabetically sorted")
        
        # Ensure gpt-4o is included (either it was in the original list or we added it)
        self.assertIn('gpt-4o', result, "The default gpt-4o model should always be included")
    
    @unittest.skipIf(get_all_models is None or format_models_for_selectbox is None,
                     "Models utility functions not available")
    def test_format_models_for_selectbox_includes_default(self):
        """Test that format_models_for_selectbox includes the default model."""
        # Get all models
        all_models = get_all_models()
        
        # Get formatted models
        formatted_models = format_models_for_selectbox()
        
        # Check that the default model is included
        self.assertIn('gpt-4o', formatted_models, "gpt-4o should be included in formatted models")
        
        # Check that all models are included
        self.assertEqual(len(formatted_models), len(all_models), 
                        "format_models_for_selectbox should include all models")

if __name__ == '__main__':
    unittest.main()