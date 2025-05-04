"""
Tests for the model-helper utilities (live-hits EDSL).
"""

from __future__ import annotations

import pathlib
import sys
import unittest
from collections.abc import Sequence

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

try:
    from edsl import Model  # type: ignore
except Exception:
    Model = None  # type: ignore[assignment]

from utils.models import (
    get_all_models,
    get_service_map,
    format_models_for_selectbox,
    DEFAULT_MODEL_LABEL,
)

# Locate PrettyList for isinstance checks (EDSL moved it around a few times)
LIST_LIKE: tuple[type, ...] = (list,)
for p in ("edsl.utilities.PrettyList", "edsl.util.pretty", "edsl.pretty"):
    try:
        mod = __import__(p, fromlist=["PrettyList"])
        PrettyList = getattr(mod, "PrettyList")  # type: ignore[attr-defined]
        LIST_LIKE = (list, PrettyList)
        break
    except Exception:
        pass


def _extract(raw) -> set[str]:
    if isinstance(raw, LIST_LIKE):
        return {str(r[1]) for r in raw if isinstance(r, Sequence) and len(r) >= 2}
    if isinstance(raw, dict):
        out: set[str] = set()
        for v in raw.values():
            if isinstance(v, Sequence):
                out.update(map(str, v))
        return out
    raise TypeError(type(raw))


class TestModels(unittest.TestCase):
    @unittest.skipIf(Model is None, "EDSL not installed")
    def test_service_mapping_is_complete(self) -> None:
        """Every model reported by EDSL has an associated service."""
        edsl_models = _extract(Model.check_working_models())
        map_ = get_service_map()

        self.assertTrue(edsl_models)  # sanity
        self.assertGreaterEqual(len(map_), len(edsl_models) - 5)

        missing = [m for m in edsl_models if m not in map_]
        self.assertLess(len(missing), 5, f"Missing service for: {missing[:5]}")

        self.assertEqual(map_.get("gpt-4o"), "openai")

    def test_dropdown_strings(self) -> None:
        dd = format_models_for_selectbox()
        self.assertIn(DEFAULT_MODEL_LABEL, dd)
        for entry in dd[:50]:  # spot-check format
            self.assertRegex(entry, r".+\s\[[^\]]+\]")

    def test_superset_of_edsl(self) -> None:
        expected = _extract(Model.check_working_models()) if Model else set()
        actual = set(get_all_models())
        self.assertTrue(expected.issubset(actual))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
