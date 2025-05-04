#!/usr/bin/env python3
"""
Troubleshooting tool for the model dropdown.

This script helps debug why the model dropdown might only be showing gpt-4o.
It checks various potential issues and provides guidance on how to fix them.
"""
import os
import sys
import logging
import importlib.util

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

print("\n==== love.dj Model Dropdown Troubleshooter ====\n")

# Check if the script is being run from the project root
print("1. Checking script location...", end=" ")
if not os.path.exists("app.py") or not os.path.exists("src"):
    print("❌ FAIL")
    print("   Error: This script should be run from the project root directory.")
    print("   Current directory:", os.getcwd())
    print("   Please run: cd /path/to/love.dj && python3 troubleshoot.py")
    sys.exit(1)
print("✅ OK")

# Check if EDSL is installed
print("2. Checking EDSL installation...", end=" ")
edsl_spec = importlib.util.find_spec("edsl")
if edsl_spec is None:
    print("❌ FAIL")
    print("   Error: EDSL is not installed.")
    print("   Please run: pip install edsl")
    print("   If you're using a virtual environment, make sure it's activated.")
    sys.exit(1)
print("✅ OK")

# Check if Model is available in EDSL
print("3. Checking EDSL Model class...", end=" ")
try:
    from edsl import Model
    print("✅ OK")
except ImportError as e:
    print("❌ FAIL")
    print(f"   Error: Could not import Model from EDSL: {e}")
    print("   Please check your EDSL installation.")
    sys.exit(1)

# Try calling check_working_models
print("4. Checking Model.check_working_models()...", end=" ")
try:
    models_by_provider = Model.check_working_models()
    print("✅ OK")
except Exception as e:
    print("❌ FAIL")
    print(f"   Error: Failed to call Model.check_working_models(): {e}")
    print("   Please check your EDSL configuration and API credentials.")
    sys.exit(1)

# Check the type of the result
print("5. Checking result type...", end=" ")
if not isinstance(models_by_provider, dict):
    print("❌ FAIL")
    print(f"   Error: Model.check_working_models() returned {type(models_by_provider)} instead of dict.")
    print(f"   Value: {models_by_provider}")
    sys.exit(1)
print("✅ OK")

# Check if there are any providers
print("6. Checking providers...", end=" ")
if not models_by_provider:
    print("❌ FAIL")
    print("   Error: No providers returned from Model.check_working_models().")
    print("   Please check your EDSL configuration and API credentials.")
    sys.exit(1)
print(f"✅ OK - Found {len(models_by_provider)} providers")

# Check if there are any models
all_models = []
for provider, models in models_by_provider.items():
    if isinstance(models, list):
        all_models.extend(models)

print("7. Checking models count...", end=" ")
if not all_models:
    print("❌ FAIL")
    print("   Error: No models found in any provider.")
    print("   Provider data:", models_by_provider)
    sys.exit(1)
print(f"✅ OK - Found {len(all_models)} models")

# Check our utility functions
print("8. Checking model utility functions...", end=" ")
try:
    from src.utils.models import get_all_models, format_models_for_selectbox
    print("✅ OK")
except ImportError as e:
    print("❌ FAIL")
    print(f"   Error: Could not import model utilities: {e}")
    print("   Please check your project structure.")
    sys.exit(1)

# Check get_all_models
print("9. Testing get_all_models()...", end=" ")
try:
    result = get_all_models()
    if len(result) <= 1:
        print("❌ FAIL")
        print(f"   Error: get_all_models() only returned {len(result)} model(s): {result}")
        print("   But Model.check_working_models() returned {len(all_models)} models.")
        print("   This suggests a bug in get_all_models().")
        sys.exit(1)
    print(f"✅ OK - Returned {len(result)} models")
except Exception as e:
    print("❌ FAIL")
    print(f"   Error: Exception in get_all_models(): {e}")
    print("   Please check the implementation of get_all_models().")
    sys.exit(1)

# Check format_models_for_selectbox
print("10. Testing format_models_for_selectbox()...", end=" ")
try:
    formatted = format_models_for_selectbox()
    if len(formatted) <= 1:
        print("❌ FAIL")
        print(f"   Error: format_models_for_selectbox() only returned {len(formatted)} model(s): {formatted}")
        print("   But get_all_models() returned {len(result)} models.")
        print("   This suggests a bug in format_models_for_selectbox().")
        sys.exit(1)
    print(f"✅ OK - Returned {len(formatted)} models")
except Exception as e:
    print("❌ FAIL")
    print(f"   Error: Exception in format_models_for_selectbox(): {e}")
    print("   Please check the implementation of format_models_for_selectbox().")
    sys.exit(1)

# All checks passed
print("\n✅ ALL CHECKS PASSED")
print(f"Found {len(models_by_provider)} providers with {len(all_models)} models.")
print(f"get_all_models() returned {len(result)} models.")
print(f"format_models_for_selectbox() returned {len(formatted)} models.")

# Show sample models
print("\nSample models from EDSL (first 10):")
for i, model in enumerate(sorted(all_models)[:10]):
    print(f"  {i+1}. {model}")

print("\nIf the Streamlit dropdown is still only showing gpt-4o:")
print("1. Make sure you're running the latest version of the code")
print("2. Check the edsl_models.log file for any errors")
print("3. Try restarting the Streamlit app")
print("4. Try clearing your browser cache or using a private browsing window")
print("5. Make sure your Streamlit app is using the updated model utils")

print("\nYou might see different models in the dropdown because:")
print("- Your EDSL configuration/API keys might only have access to certain models")
print("- The available models might change over time as providers update their offerings")
print("- Different environments might have different EDSL versions or configurations")

print("\nFor more detailed debugging, run:")
print("python3 debug_models.py > models_debug.log 2>&1")