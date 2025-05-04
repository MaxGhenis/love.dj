# app.py
"""
Tiny wrapper so `streamlit run app.py` still works.

All UI logic lives in *src/ui/layout.py*.
"""

from src.ui.layout import main

if __name__ == "__main__":
    main()
