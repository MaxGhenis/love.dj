"""
Utility helpers around EDSL’s `Model.check_working_models()`.

✅  Works with all known EDSL formats:
    • PrettyList / plain list → [[provider, model_name, …], …]
    • Legacy dict            → {provider: [model_name, …], …}
"""

from __future__ import annotations

import inspect
import logging
import os
from collections.abc import Sequence
from typing import List, Set

# --------------------------------------------------------------------------- #
#  Logging                                                                     #
# --------------------------------------------------------------------------- #
LOGFILE = "edsl_models.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOGFILE, encoding="utf-8")],
)
log = logging.getLogger("edsl_models")
log.info("Loading models utility from: %s", os.path.abspath(__file__))

# --------------------------------------------------------------------------- #
#  EDSL import                                                                 #
# --------------------------------------------------------------------------- #
try:
    from edsl import Model  # type: ignore

    log.info("Successfully imported EDSL")
except Exception as exc:  # pragma: no cover
    Model = None  # type: ignore[assignment]
    log.error("❌  Could not import EDSL: %s", exc)


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _flatten_edsl(raw) -> list[str]:
    """
    Normalise EDSL’s output into a **flat list** of model names.
    """
    names: Set[str] = set()

    # PrettyList inherits from Sequence, so this catches both
    if isinstance(raw, Sequence):
        for row in raw:
            if isinstance(row, Sequence) and len(row) >= 2:
                names.add(str(row[1]))

    elif isinstance(raw, dict):  # very old EDSL versions
        for lst in raw.values():
            if isinstance(lst, Sequence):
                names.update(map(str, lst))

    else:
        log.error("Unknown data type from EDSL: %r", type(raw))

    return sorted(names)


# --------------------------------------------------------------------------- #
#  Public API                                                                  #
# --------------------------------------------------------------------------- #
def get_all_models() -> list[str]:
    """
    Return **all** model IDs that EDSL reports, sorted alphabetically.

    Falls back to ``['gpt-4o']`` if anything goes wrong so the Streamlit app
    never crashes.
    """
    if Model is None:  # pragma: no cover – EDSL not installed
        log.warning("EDSL missing – returning fallback list")
        return ["gpt-4o"]

    try:
        log.info("Calling Model.check_working_models()")
        raw = Model.check_working_models()
        models: List[str] = _flatten_edsl(raw)

        if not models:  # something went wrong with parsing
            raise ValueError("Parsed 0 model names")

        log.info("Found %s unique models from EDSL", len(models))
        return models

    except Exception as exc:  # pragma: no cover
        log.error("Error while fetching models: %s", exc, exc_info=True)
        return ["gpt-4o"]


def format_models_for_selectbox() -> list[str]:
    """
    Convenience helper for the Streamlit dropdown.

    Ensures ``'gpt-4o'`` is *always* present as a sane default (and first).
    """
    base = get_all_models()

    if "gpt-4o" not in base:
        base.insert(0, "gpt-4o")
    else:
        # move it to the top for UX consistency
        base = ["gpt-4o"] + [m for m in base if m != "gpt-4o"]

    log.info("Select-box list prepared with %d entries", len(base))
    return base


# --------------------------------------------------------------------------- #
#  Smoke test at import-time (helps during local dev)                          #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    pprint(format_models_for_selectbox()[:25])
