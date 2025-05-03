# app.py
import streamlit as st
from edsl import (
    Agent,  # persona container
    Model,  # wraps any LLM
    Scenario,  # lets us pipe context into the prompt
    QuestionFreeText,
    QuestionLinearScale,
)

# ──────────────────────────────── UI ────────────────────────────────
st.set_page_config(page_title="🎧 love.dj", page_icon="🎧")
st.title("🎧 love.dj")

col1, col2 = st.columns(2)
with col1:
    profile_a = st.text_area(
        "Profile A (who is *this* person?)",
        height=180,
        placeholder="e.g. 28 y o product-manager, loves jazz & climbing…",
    )
with col2:
    profile_b = st.text_area(
        "Profile B (and their date?)",
        height=180,
        placeholder="e.g. 30 y o PhD student, avid reader, vegan…",
    )

rounds = st.slider("How many back-and-forths?", 1, 6, value=3)
model_name = st.text_input("LLM to use (any model EDSL knows)", value="gpt-4o")
go = st.button("🚀 Spin the decks")


# ──────────────────────────────── back end ────────────────────────────────
def run_date(profile_a: str, profile_b: str, n_rounds: int, model_name: str):
    """Simulate a date, return transcript and ratings."""
    m = Model(model_name)  # default parameters ok :contentReference[oaicite:0]{index=0}

    agent_a = Agent(
        name="A",
        traits={
            "persona": profile_a or default_a,
            "guidelines": (
                "Speak casually, in first-person, as if you’re meeting for the first time. "
                "Do **not** dump your full résumé; reveal details gradually and ask questions. "
                "Feel free to use humour or small-talk."
            ),
        },
    )
    agent_b = Agent(
        name="B",
        traits={
            "persona": profile_b or default_b,
            "guidelines": agent_a.traits["guidelines"],
        },
    )

    transcript = []  # list[(speaker, text)]
    history_txt = ""

    # Seed opener from A so the loop is symmetric
    opener = (
        QuestionFreeText(
            question_name="opener",
            question_text="Introduce yourself and ask an opening question.",
        )
        .by(m)
        .by(agent_a)
        .run()
        .select("opener")
        .first()
    )
    transcript.append(("A", opener))
    history_txt += f"A: {opener}\n"

    # ---------- conversation loop ----------
    for turn in range(n_rounds):
        for speaker, agent_self, agent_other in [
            ("B", agent_b, agent_a),
            ("A", agent_a, agent_b),
        ]:
            scenario = Scenario(
                {
                    "chat": history_txt.strip(),
                    "persona": agent_self.traits["persona"],
                    "partner_persona": agent_other.traits["persona"],
                }
            )

            q = QuestionFreeText(
                question_name=f"turn_{turn}_{speaker}",
                question_text=(
                    "You are {{ persona }} on a first date.\n\n"
                    "{{ chat }}\n\n"
                    "Respond in character (≤ 120 words)."
                ),
            )

            answer = (
                q.by(Model(model_name))
                .by(agent_self)
                .by(scenario)
                .run()
                .select(f"turn_{turn}_{speaker}")
                .first()
            )
            transcript.append((speaker, answer))
            history_txt += f"{speaker}: {answer}\n"

    # ---------- each agent rates the date ----------
    rating_question = QuestionLinearScale(
        question_name="rating",
        question_text=(
            "{{ history }}\n\n"
            "On a scale of 1–10, how would you rate this date? "
            "(1 = Terrible • 10 = Amazing)\n"
            "Respond with just the number."
        ),
        question_options=list(range(1, 11)),  # 1-10 inclusive
        option_labels={1: "Terrible", 10: "Amazing"},
    )

    rating_a = int(
        rating_question.by(Model(model_name))
        .by(agent_a)
        .by(Scenario({"history": history_txt}))
        .run()
        .select("rating")
        .first()
    )

    rating_b = int(
        rating_question.by(Model(model_name))
        .by(agent_b)
        .by(Scenario({"history": history_txt}))
        .run()
        .select("rating")
        .first()
    )

    return transcript, rating_a, rating_b


# ──────────────────────────────── run & show ────────────────────────────────
if go:
    with st.spinner("Mixing…"):
        transcript, score_a, score_b = run_date(
            profile_a, profile_b, rounds, model_name
        )

    st.subheader("💬 Transcript")
    for speaker, line in transcript:
        st.markdown(f"**{speaker}:** {line}")

    st.subheader("⭐ Ratings")
    st.markdown(f"**A’s score:** {score_a} / 10")
    st.markdown(f"**B’s score:** {score_b} / 10")
    st.markdown(f"**Average:** {(score_a+score_b)/2:.1f} / 10")

    st.caption(
        "Powered by EDSL – agents, scenarios & questions handle the heavy lifting of multi-agent dialogue :contentReference[oaicite:2]{index=2}"
    )
