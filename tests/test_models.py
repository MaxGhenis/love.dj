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
        
        # Verify it returns a dictionary
        self.assertIsInstance(raw_models, dict, "EDSL should return a dictionary of providers to models")
        
        # Make sure it contains models we expect
        all_models = []
        for provider_models in raw_models.values():
            if isinstance(provider_models, list):
                all_models.extend(provider_models)
                
        # Remove duplicates
        unique_models = set(all_models)
        
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
        # Get models directly from EDSL for comparison
        raw_models = Model.check_working_models()
        
        # Calculate expected count of models
        expected_models = set()
        for provider, models in raw_models.items():
            if isinstance(models, list):
                expected_models.update(models)
        
        # Call our function
        result = get_all_models()
        
        # Check that the length of our result matches what we expect
        # (Allowing for the addition of gpt-4o if it wasn't in the original set)
        expected_count = len(expected_models)
        self.assertGreaterEqual(len(result), expected_count, 
                               f"get_all_models should return at least {expected_count} models")
        
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