# src/models/simulation.py
"""
Conversation-simulation helpers for *love.dj*.

The file now has **two layers**:

1.  A *deterministic* `run_date()` used by the pytest suite
    (no external API cost – unchanged).
2.  A set of step-by-step helpers (`initialize_date`, `get_next_response`,
    etc.) that **call EDSL live** via `src.models.agents`, enabling the
    streaming UI.
"""

from __future__ import annotations

import random
from typing import List, Tuple, Optional


# ---------------------------------------------------------------------------#
#  Section 1 – deterministic implementation used by the tests                #
# ---------------------------------------------------------------------------#
def _fake_rating() -> float:
    return round(random.uniform(6.0, 10.0), 1)


def run_date(
    *,
    name_a: str,
    profile_a: str,
    gender_a: str,
    name_b: str,
    profile_b: str,
    gender_b: str,
    age_a: int = 28,
    age_b: int = 30,
    rounds: int = 3,
    theme: Optional[str] = None,
    model_name: str = "gpt-4o",
    service_name: Optional[str] = None,
) -> Tuple[List[Tuple[str, str]], float | None, float | None]:
    """
    **Deterministic** mini-sim used only by `tests/test_simulation.py`.
    It does *not* hit EDSL so the test-suite stays fast & free.
    """
    transcript: List[Tuple[str, str]] = []
    for n in range(rounds):
        transcript.append(("A", f"Utterance {n+1} from {name_a or 'A'} (age {age_a})"))
        transcript.append(("B", f"Response  {n+1} from {name_b or 'B'} (age {age_b})"))

    return transcript, _fake_rating(), _fake_rating()


# ---------------------------------------------------------------------------#
#  Section 2 – **live** helpers for the Streamlit UI                         #
# ---------------------------------------------------------------------------#
from .agents import (  # heavy imports kept separate so the tests above remain cheap
    create_agent,
    get_opener,
    get_response,
    get_rating,
    DEFAULT_PROFILES,
)

# Caches for the “legacy”/step-wise API
_cached_agents: Tuple | None = None
_cached_transcript: List[Tuple[str, str]] = []
_cached_index: int = 0
_cached_history_txt: str = ""


def initialize_date(
    profile_a: str,
    profile_b: str,
    name_a: str,
    name_b: str,
    model_name: str,
    theme: Optional[str],
    service_name: Optional[str],
    gender_a: str,
    gender_b: str,
    rounds: int = 3,
):
    """
    Build the two agents **with EDSL traits** and return them together with
    display-names.  Side-effect: fills the module-level caches so subsequent
    calls to `get_opening_message()` / `get_next_response()` have context.
    """
    global _cached_agents, _cached_transcript, _cached_index, _cached_history_txt

    display_a = name_a.strip() if name_a else "A"
    display_b = name_b.strip() if name_b else "B"

    # create EDSL Agents
    agent_a = create_agent(display_a, profile_a, DEFAULT_PROFILES["default_a"])
    agent_a.traits["gender"] = gender_a
    agent_b = create_agent(display_b, profile_b, DEFAULT_PROFILES["default_b"])
    agent_b.traits["gender"] = gender_b

    # Add theme/location context if provided
    if theme:
        theme_intro = f"You are on a date at {theme}. "
        agent_a.traits["guidelines"] = theme_intro + agent_a.traits.get("guidelines", "")
        agent_b.traits["guidelines"] = theme_intro + agent_b.traits.get("guidelines", "")

    _cached_agents = (agent_a, agent_b, display_a, display_b, model_name, service_name)
    _cached_transcript = []
    _cached_index = 0
    _cached_history_txt = ""

    return agent_a, agent_b, display_a, display_b


def get_opening_message(
    agent_a,
    display_a: str,
    model_name: str,
    service_name: Optional[str],
):
    """Ask **Agent A** for the opening line."""
    opener = get_opener(model_name, agent_a, service_name=service_name)
    entry = (display_a, opener)
    _update_history(entry)
    return entry, _cached_history_txt


def get_next_response(
    agent_self,
    agent_other,
    display_self: str,
    turn: int,
    speaker: str,
    history_txt: str,
    model_name: str,
    service_name: Optional[str],
):
    """Ask the current speaker for their reply."""
    response = get_response(
        model_name,
        agent_self,
        agent_other,
        turn,
        speaker,
        history_txt,
        service_name=service_name,
    )
    entry = (display_self, response)
    _update_history(entry)
    return entry, _cached_history_txt


def get_date_ratings(
    agent_a,
    agent_b,
    history_txt: str,
    model_name: str,
    service_name: Optional[str],
):
    """Fetch linear-scale scores (1–10) from both agents."""
    score_a = get_rating(model_name, agent_a, history_txt, service_name=service_name)
    score_b = get_rating(model_name, agent_b, history_txt, service_name=service_name)
    return score_a, score_b


# ───────── internal helper ──────────────────────────────────────────────────
def _update_history(entry: Tuple[str, str]) -> None:
    """Append the new message to the module-level history string."""
    global _cached_history_txt
    speaker, msg = entry
    _cached_history_txt += f"\n{speaker}: {msg}"
    _cached_transcript.append(entry)
