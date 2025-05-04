# src/ui/transcript.py
import streamlit as st
from typing import List, Tuple


def create_real_time_transcript_container():
    """Return (container, placeholders, messages)."""
    st.subheader("💬 Transcript")
    container = st.container()
    placeholders: List[st.delta_generator.DeltaGenerator] = []
    messages: List[Tuple[str, str]] = []
    return container, placeholders, messages


def update_transcript(
    container,
    placeholders,
    messages,
    speaker: str,
    text: str,
    gender_a="he/him",
    gender_b="she/her",
):
    """Append a new line of dialogue to the transcript."""
    # pick or make placeholder
    if len(placeholders) <= len(messages):
        placeholders.append(container.empty())
    ph = placeholders[len(messages)]

    # quick emoji from pronouns
    def emoji(gen: str) -> str:
        return {"he/him": "👨", "she/her": "👩"}.get(gen, "🧑")

    icon = emoji(gender_a if speaker == "A" else gender_b)

    ph.markdown(f"**{icon} {speaker}:** {text}")
    messages.append((speaker, text))
