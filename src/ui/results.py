# src/ui/results.py
import streamlit as st
from typing import List, Tuple


def display_results(
    transcript: List[Tuple[str, str]],
    score_a: float | None,
    score_b: float | None,
    name_a: str,
    name_b: str,
    model_name: str,
):
    """Show transcript and (optionally) the scores."""
    st.success(f"Simulated with **{model_name}**")

    st.subheader("Conversation")
    for who, line in transcript:
        st.markdown(f"**{who}:** {line}")

    if score_a is not None and score_b is not None:
        st.subheader("⭐ Ratings")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"{name_a or 'A'}", f"{score_a}/10")
        c2.metric(f"{name_b or 'B'}", f"{score_b}/10")
        c3.metric("Average", f"{(score_a + score_b)/2:.1f}/10")
