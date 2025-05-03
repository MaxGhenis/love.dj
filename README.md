# love.dj

A dating simulator powered by AI that simulates conversations between two people on a first date.

## Features

- Create profiles for two people and simulate their first date conversation
- Add names for the participants to make the conversation more personalized
- Set the number of back-and-forth exchanges
- Choose which language model to use
- Set an optional location or theme for the date
- Get ratings from both participants on how the date went

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## API Key Setup

The application requires API keys to use language models through EDSL:

### Local Development

1. Create a `.streamlit/secrets.toml` file in your project directory
2. Use the `secrets.toml.example` file as a template
3. Add your EDSL API key and any model provider API keys you want to use

Example `.streamlit/secrets.toml`:
```toml
[edsl]
api_key = "your-edsl-api-key-here"

[edsl.openai]
api_key = "your-openai-api-key-here"
```

### Streamlit Community Cloud Deployment

1. Go to your app's settings in Streamlit Community Cloud
2. Navigate to the "Secrets" section
3. Add your secrets in the same format as the `.streamlit/secrets.toml` file

## Usage

Run the application with:

```
streamlit run app.py
```

Then open your browser to the URL shown in the console (typically http://localhost:8501).

## Project Structure

- `app.py` - Main entry point for the Streamlit application
- `src/` - Source code directory
  - `models/` - Contains the agent and simulation logic
    - `agents.py` - Agent creation and interaction functions
    - `simulation.py` - Core date simulation logic
  - `ui/` - User interface components
    - `streamlit_app.py` - Streamlit UI setup and display functions
- `tests/` - Unit tests
  - `test_agents.py` - Tests for agent functionality
  - `test_simulation.py` - Tests for simulation logic

## Testing

Run tests with pytest:

```
pytest
```

## Credits

Built with [Streamlit](https://streamlit.io/) and [EDSL](https://github.com/expectedparrot/edsl).
