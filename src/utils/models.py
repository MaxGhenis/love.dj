"""
Helpers around EDSL Model plus a tiny registry of *service ⇄ model* pairs.

• get_all_models()               → flat, sorted list of model IDs
• get_service_map()              → {model_id: service_name}
• format_models_for_selectbox()  → human-friendly strings for a Streamlit box
"""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from typing import Dict, List, Set, Tuple

# --------------------------------------------------------------------------- #
#  Logging                                                                    #
# --------------------------------------------------------------------------- #
FILE = os.path.abspath(__file__)
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("edsl_models.log", "a")],
    format="%(asctime)s  %(levelname)s  %(name)s  %(message)s",
)
log = logging.getLogger("edsl_models")
log.info("Loaded helper module from %s", FILE)

# --------------------------------------------------------------------------- #
#  EDSL import                                                                #
# --------------------------------------------------------------------------- #
try:
    from edsl import Model  # type: ignore
except Exception as exc:  # pragma: no cover
    log.error("Could not import EDSL: %s", exc)
    Model = None  # type: ignore[assignment]


# --------------------------------------------------------------------------- #
#  Internal normalisation helpers                                             #
# --------------------------------------------------------------------------- #
def _normalise(raw) -> Tuple[List[str], Dict[str, str]]:
    """
    Convert whatever `Model.check_working_models()` returns to

        (sorted_unique_models, {model → service})
    """
    names: Set[str] = set()
    svc_map: Dict[str, str] = {}

    # PrettyList inherits from list/Sequence, so this covers legacy & new
    if isinstance(raw, Sequence):
        for row in raw:
            if isinstance(row, Sequence) and len(row) >= 2:
                provider, model_id = row[0], str(row[1])
                names.add(model_id)
                svc_map.setdefault(model_id, provider)

    elif isinstance(raw, dict):  # very old EDSL
        for provider, lst in raw.items():
            if isinstance(lst, Sequence):
                for model_id in lst:
                    names.add(str(model_id))
                    svc_map.setdefault(str(model_id), provider)

    else:
        log.error("Unknown structure from EDSL: %r", type(raw))

    return sorted(names), svc_map


# --------------------------------------------------------------------------- #
#  Public API                                                                 #
# --------------------------------------------------------------------------- #
_SERVICE_CACHE: Dict[str, str] | None = None  # lazy singleton
_MODEL_CACHE: List[str] | None = None


def get_all_models() -> List[str]:
    """Alphabetical list of every model EDSL reports (no services)."""
    global _MODEL_CACHE, _SERVICE_CACHE

    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    if Model is None:  # pragma: no cover
        log.warning("EDSL missing – using fallback list")
        _MODEL_CACHE, _SERVICE_CACHE = ["gpt-4o"], {"gpt-4o": "openai"}
        return _MODEL_CACHE

    try:
        raw = Model.check_working_models()
        models, _SERVICE_CACHE = _normalise(raw)
        if not models:
            raise ValueError("Parsed zero models")
        _MODEL_CACHE = models
        log.info("Discovered %d unique models", len(models))
        return models
    except Exception as exc:  # pragma: no cover
        log.error("Failed to fetch models: %s", exc, exc_info=True)
        _MODEL_CACHE, _SERVICE_CACHE = ["gpt-4o"], {"gpt-4o": "openai"}
        return _MODEL_CACHE


def get_service_map() -> Dict[str, str]:
    """Return ``{model_id: service_name}``."""
    if _SERVICE_CACHE is None:
        get_all_models()  # populates the cache
    return _SERVICE_CACHE or {}


def format_models_for_selectbox() -> List[str]:
    """
    Produce strings like  ``"gpt-4o  [openai]"`` for a Streamlit selectbox.

    • Always includes **gpt-4o** and puts it on top for UX consistency.
    """
    models = get_all_models()
    svc = get_service_map()

    labelled = [f"{m} [{svc.get(m,'?')}]" for m in models]
    labelled = sorted(labelled, key=lambda s: s.lower())

    # guarantee default at top
    default = "gpt-4o [openai]"
    if default in labelled:
        labelled.remove(default)
    labelled.insert(0, default)

    log.info("Prepared %d select-box entries", len(labelled))
    return labelled


# --------------------------------------------------------------------------- #
#  Quick smoke test (only when run directly)                                  #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    pprint(format_models_for_selectbox()[:30])

# (append to the end of src/utils/models.py)


# --------------------------------------------------------------------------- #
#  Provider-lookup helper                                                     #
# --------------------------------------------------------------------------- #
def get_service_map() -> dict[str, str]:
    """
    Return a cached dict mapping **model_id ➜ provider/service name**.

    Useful for attaching the correct `service_name` when constructing `Model`.
    """
    global _SERVICE_CACHE  # type: ignore
    try:  # already built?
        return _SERVICE_CACHE
    except NameError:
        raw = Model.check_working_models()
        mapping: dict[str, str] = {}

        if isinstance(raw, list):
            for provider, model, *_ in raw:
                mapping[str(model)] = str(provider)
        elif isinstance(raw, dict):
            for provider, models in raw.items():
                for m in models:
                    mapping[str(m)] = str(provider)

        _SERVICE_CACHE = mapping
        logger.info(f"Built service map with {len(mapping)} entries")
        return mapping
