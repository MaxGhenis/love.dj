# src/models/agents.py
"""
Agent helpers and prompting logic for *love.dj*.

Public API
----------
create_agent(...)    → returns an EDSL Agent with persona + guidelines
get_opener(...)      → first line of the date
get_response(...)    → subsequent replies
get_rating(...)      → 1-10 score from the agent at the end
"""

from edsl import (
    Agent,
    Model,
    Scenario,
    QuestionFreeText,
    QuestionLinearScale,
)

# Prompt text is centralised in src/prompts/date.py
from src.prompts.date import GUIDELINES, OPENING_PROMPT, RESPONSE_PROMPT, RATING_PROMPT

# ---------------------------------------------------------------------------#
#  Default personas (used when the user leaves the profile box empty)        #
# ---------------------------------------------------------------------------#
DEFAULT_PROFILES = {
    "default_a": (
        "28-year-old product manager in San Francisco. Loves jazz, weekend rock-climbing, "
        "and hunting for the best under-the-radar restaurants. Looking for an adventurous partner "
        "with a playful sense of humour."
    ),
    "default_b": (
        "30-year-old PhD student in literature. Avid reader who practises yoga to unwind and is a committed vegan. "
        "Enjoys deep conversations, quiet coffee shops, and authenticity in relationships."
    ),
}


# ---------------------------------------------------------------------------#
#  Public helpers                                                            #
# ---------------------------------------------------------------------------#
def create_agent(name: str, profile: str, default_profile: str) -> Agent:
    """Return an EDSL Agent with persona + conversation guidelines."""
    return Agent(
        name=name,
        traits={
            "persona": profile or default_profile,
            "guidelines": GUIDELINES,
        },
    )


# ---------------------------------------------------------------------------#
#  Turn helpers                                                              #
# ---------------------------------------------------------------------------#
def _build_model(model_name: str, service_name: str | None) -> Model:
    return (
        Model(model_name, service_name=service_name)
        if service_name
        else Model(model_name)
    )


def get_opener(
    model_name: str, agent: Agent, *, service_name: str | None = None
) -> str:
    """First message on the date."""
    model = _build_model(model_name, service_name)

    scenario_fields = {"persona": agent.traits["persona"]}
    if "gender" in agent.traits:
        scenario_fields["gender"] = agent.traits["gender"]

    return (
        QuestionFreeText("opener", OPENING_PROMPT)
        .by(model)
        .by(agent)
        .by(Scenario(scenario_fields))
        .run()
        .select("opener")
        .first()
    )


def get_response(
    model_name: str,
    agent_self: Agent,
    agent_other: Agent,
    turn: int,
    speaker: str,
    history_txt: str,
    *,
    service_name: str | None = None,
) -> str:
    """Generate the next reply given the conversation so far."""
    model = _build_model(model_name, service_name)

    scenario_fields = {
        "chat": history_txt.strip(),
        "persona": agent_self.traits["persona"],
        "partner_persona": agent_other.traits["persona"],
        "gender": agent_self.traits.get("gender", "he/him"),
        "partner_gender": agent_other.traits.get("gender", "she/her"),
    }

    return (
        QuestionFreeText(f"turn_{turn}_{speaker}", RESPONSE_PROMPT)
        .by(model)
        .by(agent_self)
        .by(Scenario(scenario_fields))
        .run()
        .select(f"turn_{turn}_{speaker}")
        .first()
    )


def get_rating(
    model_name: str,
    agent: Agent,
    history_txt: str,
    *,
    service_name: str | None = None,
) -> int:
    """Ask the agent to rate the date on a 1-10 scale."""
    model = _build_model(model_name, service_name)

    result = (
        QuestionLinearScale(
            question_name="rating",
            question_text=RATING_PROMPT,
            question_options=list(range(1, 11)),  # 1-10 inclusive
            option_labels={1: "Terrible", 10: "Amazing"},
        )
        .by(model)
        .by(agent)
        .by(Scenario({"history": history_txt}))
        .run()
        .select("rating")
        .first()
    )

    # Robust parsing to ensure we always return an int 1-10
    try:
        return int(result)  # type: ignore[arg-type]
    except Exception:
        import re

        numbers = re.findall(r"\d+", str(result) if result is not None else "")
        return int(numbers[0]) if numbers else 5  # default midpoint
