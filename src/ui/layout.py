# src/ui/layout.py
"""
Streamlit front-end that **streams** each EDSL reply.

It uses the live helpers from `src.models.simulation` and the small
avatar/emoji transcript UI from `src.ui.transcript`.
"""
from __future__ import annotations

import time
import streamlit as st
from typing import List, Tuple

from src.utils.models import format_models_for_selectbox, get_service_map
from src.ui.transcript import (
    create_real_time_transcript_container,
    update_transcript,
)
from src.ui.results import display_results
from src.models.simulation import (
    initialize_date,
    get_opening_message,
    get_next_response,
    get_date_ratings,
)


# ────────────────────────────────────────────────────────────────────────────
def _form() -> dict:
    """Render input widgets and return the selections."""
    st.set_page_config(page_title="🎧 love.dj", page_icon="🎧")
    st.title("🎧 love.dj")

    # profiles ---------------------------------------------------------------
    c1, c2 = st.columns(2)
    with c1:
        name_a = st.text_input("Person A’s name")
        gender_a = st.selectbox(
            "Person A’s pronouns", ["he/him", "she/her", "they/them"]
        )
        profile_a = st.text_area("Profile A", height=140)

    with c2:
        name_b = st.text_input("Person B’s name")
        gender_b = st.selectbox(
            "Person B’s pronouns", ["he/him", "she/her", "they/them"], index=1
        )
        profile_b = st.text_area("Profile B", height=140)

    # date settings ----------------------------------------------------------
    st.subheader("Date settings")
    c3, c4 = st.columns(2)
    with c3:
        rounds = st.slider("Back-and-forth rounds", 1, 6, 3)

        opts = format_models_for_selectbox()
        default_ix = opts.index("gpt-4o [openai]") if "gpt-4o [openai]" in opts else 0
        chosen = st.selectbox("Language model", opts, index=default_ix)
        model_name = chosen.rsplit(" ", 1)[0]  # strip " [provider]"

    with c4:
        theme = st.text_input("Location / theme (optional)")

    go = st.button("🚀 Spin the decks")

    return dict(
        name_a=name_a,
        profile_a=profile_a,
        gender_a=gender_a,
        name_b=name_b,
        profile_b=profile_b,
        gender_b=gender_b,
        rounds=rounds,
        theme=theme,
        model_name=model_name,
        go=go,
    )


# ────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ui = _form()
    if not ui["go"]:
        return

    # provider lookup --------------------------------------------------------
    provider_map = get_service_map()
    service = provider_map.get(ui["model_name"])
    if service is None:
        st.error("Couldn’t find which service hosts that model. Pick another.")
        return

    st.info(f"Using **{ui['model_name']}** via *{service}* service …")

    # transcript container ---------------------------------------------------
    container, placeholders, messages = create_real_time_transcript_container()

    # initialise agents & opener --------------------------------------------
    agent_a, agent_b, disp_a, disp_b = initialize_date(
        ui["profile_a"],
        ui["profile_b"],
        ui["name_a"],
        ui["name_b"],
        ui["model_name"],
        ui["theme"],
        service,
        ui["gender_a"],
        ui["gender_b"],
        ui["rounds"],
    )

    opener_entry, history = get_opening_message(
        agent_a, disp_a, ui["model_name"], service
    )
    update_transcript(
        container,
        placeholders,
        messages,
        "A",
        opener_entry[1],
        ui["gender_a"],
        ui["gender_b"],
    )

    # dialogue rounds --------------------------------------------------------
    for turn in range(ui["rounds"]):
        time.sleep(0.4)

        # B’s reply
        b_entry, history = get_next_response(
            agent_b,
            agent_a,
            disp_b,
            turn,
            "B",
            history,
            ui["model_name"],
            service,
        )
        update_transcript(
            container,
            placeholders,
            messages,
            "B",
            b_entry[1],
            ui["gender_a"],
            ui["gender_b"],
        )

        time.sleep(0.4)

        # A’s reply
        a_entry, history = get_next_response(
            agent_a,
            agent_b,
            disp_a,
            turn,
            "A",
            history,
            ui["model_name"],
            service,
        )
        update_transcript(
            container,
            placeholders,
            messages,
            "A",
            a_entry[1],
            ui["gender_a"],
            ui["gender_b"],
        )

    # ratings ----------------------------------------------------------------
    score_a, score_b = get_date_ratings(
        agent_a, agent_b, history, ui["model_name"], service
    )

    display_results(
        transcript=[],  # we already printed lines live
        score_a=score_a,
        score_b=score_b,
        name_a=ui["name_a"],
        name_b=ui["name_b"],
        model_name=ui["model_name"],
    )


# convenience:  python -m src.ui.layout  -> launches Streamlit
if __name__ == "__main__":
    import sys, streamlit.web.cli as stcli

    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())

# ------------------------------------------------------------------ #
#  Back-compat: keep the old public name “setup_ui”                  #
# ------------------------------------------------------------------ #
setup_ui = _form  # ← add this line
