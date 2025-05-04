"""
Integration tests for the model helpers.

They *hit the live EDSL API*, so make sure your EDSL credentials /
environment variables are configured before running `pytest`.
"""

from __future__ import annotations

import pathlib
import sys
import unittest
from collections.abc import Sequence

# --------------------------------------------------------------------------- #
#  Dynamic import path handling                                                #
# --------------------------------------------------------------------------- #
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))  # so `import utils.models` works

# --------------------------------------------------------------------------- #
#  Imports                                                                     #
# --------------------------------------------------------------------------- #
try:
    from edsl import Model  # type: ignore
except Exception:
    Model = None  # type: ignore[assignment]

from utils.models import get_all_models, format_models_for_selectbox  # noqa: E402

# locate PrettyList for isinstance checks (EDSL has moved it around)
LIST_LIKE: tuple[type, ...] = (list,)
for modpath in (
    "edsl.utilities.PrettyList",
    "edsl.util.pretty",
    "edsl.pretty",
):
    try:
        mod = __import__(modpath, fromlist=["PrettyList"])
        PrettyList = getattr(mod, "PrettyList")  # type: ignore[attr-defined]
        LIST_LIKE = (list, PrettyList)
        break
    except Exception:
        continue


# --------------------------------------------------------------------------- #
#  Helper                                                                      #
# --------------------------------------------------------------------------- #
def extract_model_names(raw) -> set[str]:
    """
    Pull **model names** out of EDSL’s heterogeneous structures.
    """
    names: set[str] = set()

    if isinstance(raw, LIST_LIKE):
        for row in raw:
            if isinstance(row, Sequence) and len(row) >= 2:
                names.add(str(row[1]))

    elif isinstance(raw, dict):
        for lst in raw.values():
            if isinstance(lst, Sequence):
                names.update(map(str, lst))

    else:  # totally new structure – fail fast
        raise TypeError(f"Unsupported EDSL payload type: {type(raw)!r}")

    return names


# --------------------------------------------------------------------------- #
#  Tests                                                                       #
# --------------------------------------------------------------------------- #
class TestModels(unittest.TestCase):
    @unittest.skipIf(Model is None, "EDSL not installed")
    def test_edsl_raw_looks_sane(self) -> None:
        raw = Model.check_working_models()
        self.assertIsInstance(raw, (dict, Sequence))

        models = extract_model_names(raw)
        self.assertGreater(len(models), 10, "Suspiciously few models extracted")

    @unittest.skipIf(Model is None, "EDSL not installed")
    def test_get_all_models_supersets_edsl(self) -> None:
        expected = extract_model_names(Model.check_working_models())
        result = get_all_models()

        self.assertIsInstance(result, list)
        self.assertEqual(result, sorted(result))

        missing = expected.difference(result)
        loss = len(missing) / max(1, len(expected))
        self.assertLess(loss, 0.05, f"Lost too many models ({loss:.1%})")

        self.assertIn("gpt-4o", result)

    def test_selectbox_includes_default(self) -> None:
        dropdown = format_models_for_selectbox()
        self.assertIn("gpt-4o", dropdown)

        base = set(get_all_models())
        self.assertTrue(base.issubset(dropdown))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
