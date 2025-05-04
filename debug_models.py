#!/usr/bin/env python3
"""
Simple script to debug model dropdown issues.

This script tests each step of the model loading process and prints
detailed information to help diagnose problems.

Run this script in your environment to check if EDSL models are loading correctly.
"""
import sys

print("\n======== EDSL Model Debug ========")
print(f"Python version: {sys.version}")

# Step 1: Import EDSL
print("\n1. Importing EDSL...")
try:
    from edsl import Model
    print("✅ EDSL imported successfully")
except ImportError as e:
    print(f"❌ Failed to import EDSL: {e}")
    print("Make sure EDSL is installed: pip install edsl")
    sys.exit(1)

# Step 2: Check EDSL Model.check_working_models()
print("\n2. Calling Model.check_working_models()...")
try:
    edsl_result = Model.check_working_models()
    print(f"✅ Got response from EDSL: {type(edsl_result)}")
    
    # Parse model data based on response format
    all_model_names = []
    
    if isinstance(edsl_result, list):
        # Newer EDSL returns a list of model info: [[provider, model_name, ...], ...]
        print(f"EDSL returned a list with {len(edsl_result)} model entries")
        
        # Extract model names and count by provider
        provider_counts = {}
        for model_info in edsl_result:
            if isinstance(model_info, list) and len(model_info) >= 2:
                provider = model_info[0]
                model_name = model_info[1]
                
                # Count models per provider
                provider_counts[provider] = provider_counts.get(provider, 0) + 1
                
                # Add to our list of model names
                all_model_names.append(model_name)
        
        # Print provider statistics
        print(f"Found models from {len(provider_counts)} providers:")
        for provider, count in sorted(provider_counts.items()):
            print(f"  • {provider}: {count} models")
    
    elif isinstance(edsl_result, dict):
        # Older EDSL returns a dictionary: {provider: [model_names], ...}
        print(f"Found {len(edsl_result)} providers")
        
        # Count models per provider
        for provider, models in edsl_result.items():
            model_count = len(models) if isinstance(models, list) else 0
            print(f"  • {provider}: {model_count} models")
            if isinstance(models, list):
                all_model_names.extend(models)
    
    else:
        print(f"❌ Unexpected return type: {type(edsl_result)}")
        print(f"Value (sample): {str(edsl_result)[:200]}...")
        print("The rest of the analysis may not work correctly.")
    
    # Count unique models
    unique_models = set(all_model_names)
    unique_count = len(unique_models)
    print(f"Total unique models: {unique_count}")
    
    if unique_count < 10:
        print(f"⚠️ WARNING: Only found {unique_count} models - expecting 100+")
        
    # Check for common models
    common_models = ['gpt-4o', 'gpt-4-turbo', 'claude-3-opus-20240229', 'gemini-1.5-pro']
    found_models = [model for model in common_models if model in unique_models]
    missing_models = [model for model in common_models if model not in unique_models]
    
    if found_models:
        print(f"Found expected models: {', '.join(found_models)}")
    
    if missing_models:
        print(f"⚠️ Missing expected models: {', '.join(missing_models)}")
    
    # Save raw data to file for inspection
    try:
        import json
        with open("edsl_models_raw.json", "w") as f:
            json.dump(edsl_result, f, indent=2)
        print("✅ Saved raw model data to edsl_models_raw.json")
    except:
        with open("edsl_models_raw.txt", "w") as f:
            f.write(str(edsl_result))
        print("✅ Saved raw model data to edsl_models_raw.txt")
        
except Exception as e:
    print(f"❌ Error calling Model.check_working_models(): {e}")
    print("Check EDSL configuration and API credentials")
    sys.exit(1)

# Step 3: Check our utility functions
print("\n3. Testing our model utility functions...")
try:
    from src.utils.models import get_all_models, format_models_for_selectbox
    print("✅ Imported model utilities")
    
    # Test get_all_models
    print("\nTesting get_all_models()...")
    all_models = get_all_models()
    print(f"✅ Got {len(all_models)} models")
    print(f"Sample: {', '.join(all_models[:5])}...")
    
    # Test format_models_for_selectbox
    print("\nTesting format_models_for_selectbox()...")
    formatted_models = format_models_for_selectbox()
    print(f"✅ Got {len(formatted_models)} formatted models")
    print(f"First model: {formatted_models[0]}")
    
except ImportError as e:
    print(f"❌ Failed to import model utilities: {e}")
    print("Make sure you're running this script from the project root")
except Exception as e:
    print(f"❌ Error in model utilities: {e}")

print("\n======== Debug Complete ========")
print("If you're seeing models in steps 2 and 3, but not in the Streamlit app,")
print("check your Streamlit app's model dropdown implementation.")
print("If not seeing models in step 2, check your EDSL installation and API credentials.")