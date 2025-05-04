# src/ui/__init__.py
"""
Public UI façade – lets the rest of the project keep its old imports.

All helpers are re-exported so code that does
    from src.ui.streamlit_app import setup_ui, ...
continues to work.
"""

from .layout import setup_ui, main  # noqa: F401
from .transcript import (  # noqa: F401
    create_real_time_transcript_container,
    update_transcript,
)
from .results import display_results  # noqa: F401

__all__ = [
    "setup_ui",
    "main",
    "create_real_time_transcript_container",
    "update_transcript",
    "display_results",
]
