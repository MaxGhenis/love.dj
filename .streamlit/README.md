# Streamlit Configuration Directory

This directory is used for Streamlit configuration files.

## Setting up API keys

To run this application locally, create a `secrets.toml` file in this directory with your API keys:

```toml
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"

[edsl]
api_key = "your-edsl-api-key-here"

[edsl.openai]
api_key = "your-openai-api-key-here"

# Add other provider API keys as needed
```

Keep `ANTHROPIC_API_KEY` at the top level so Streamlit exports it to EDSL for
the default Sonnet model's local requests.

See the main `secrets.toml.example` file at the root of the project for a complete example.

## Streamlit Community Cloud

For deployment to Streamlit Community Cloud, add these secrets in the app settings rather than in this file.
