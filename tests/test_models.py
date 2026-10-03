"""Offline regression tests for model discovery and default-provider routing."""

from __future__ import annotations

import pathlib
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.utils import models
from src.utils.models import DEFAULT_MODEL_ID, DEFAULT_MODEL_LABEL, DEFAULT_PROVIDER


class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = Mock()
        self.rows = [
            ("example-service", "example-model"),
            (DEFAULT_PROVIDER, DEFAULT_MODEL_ID),
            ("another-service", "another-model"),
        ]
        self.registry.check_working_models.return_value = self.rows
        self.patches = [
            patch.object(models, "Model", self.registry),
            patch.object(models, "_MODEL_CACHE", None),
            patch.object(models, "_SERVICE_CACHE", None),
        ]
        for patcher in self.patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_service_mapping_is_complete(self) -> None:
        mapping = models.get_service_map()
        self.assertEqual(mapping.get(DEFAULT_MODEL_ID), DEFAULT_PROVIDER)
        for provider, model in self.rows:
            self.assertEqual(mapping[model], provider)

    def test_dropdown_strings(self) -> None:
        dropdown = models.format_models_for_selectbox()
        self.assertIn(DEFAULT_MODEL_LABEL, dropdown)
        self.assertEqual(dropdown, sorted(dropdown, key=str.lower))
        for entry in dropdown:
            self.assertRegex(entry, r".+\s\[[^\]]+\]")

    def test_superset_of_edsl(self) -> None:
        expected = {model for _, model in self.rows}
        self.assertTrue(expected.issubset(models.get_all_models()))

    def test_discovery_can_omit_default(self) -> None:
        self.registry.check_working_models.return_value = [self.rows[0]]
        self.assertEqual(
            models.get_all_models(), sorted(["example-model", DEFAULT_MODEL_ID])
        )
        self.assertEqual(models.get_service_map()[DEFAULT_MODEL_ID], DEFAULT_PROVIDER)
        self.assertIn(DEFAULT_MODEL_LABEL, models.format_models_for_selectbox())

    def test_default_uses_anthropic_even_if_registry_lists_another_provider(self) -> None:
        self.registry.check_working_models.return_value = [
            ("another-service", DEFAULT_MODEL_ID)
        ]
        self.assertEqual(models.get_service_map()[DEFAULT_MODEL_ID], DEFAULT_PROVIDER)

    def assert_default_fallback(self) -> None:
        self.assertEqual(models.get_all_models(), [DEFAULT_MODEL_ID])
        self.assertEqual(
            models.get_service_map(), {DEFAULT_MODEL_ID: DEFAULT_PROVIDER}
        )
        self.assertEqual(models.format_models_for_selectbox(), [DEFAULT_MODEL_LABEL])

    def test_missing_edsl_uses_default(self) -> None:
        with patch.object(models, "Model", None):
            self.assert_default_fallback()

    def test_discovery_failure_uses_default(self) -> None:
        self.registry.check_working_models.side_effect = RuntimeError("offline")
        with self.assertLogs("edsl_models", level="ERROR"):
            self.assert_default_fallback()

    def test_empty_registry_uses_default(self) -> None:
        self.registry.check_working_models.return_value = []
        with self.assertLogs("edsl_models", level="ERROR"):
            self.assert_default_fallback()

    def test_discovery_is_cached(self) -> None:
        models.get_all_models()
        models.get_service_map()
        models.format_models_for_selectbox()
        models.get_all_models()
        self.registry.check_working_models.assert_called_once_with()

    def test_provider_lookup_initializes_discovery(self) -> None:
        self.assertIsInstance(models.get_service_map(), dict)
        self.registry.check_working_models.assert_called_once_with()

    def test_legacy_dictionary_registry(self) -> None:
        self.registry.check_working_models.return_value = {
            "example-service": ["example-model"]
        }
        self.assertEqual(
            models.get_service_map(),
            {"example-model": "example-service", DEFAULT_MODEL_ID: DEFAULT_PROVIDER},
        )

    def test_current_edsl_model_list(self) -> None:
        from edsl.inference_services.services.anthropic_service import AnthropicService
        from edsl.language_models import LanguageModel
        from edsl.language_models.model_list import ModelList

        with patch.object(LanguageModel, "_set_key_lookup", return_value={}):
            discovered = AnthropicService.create_model("example-model")()
        self.registry.check_working_models.return_value = ModelList([discovered])

        self.assertEqual(
            models.get_all_models(), sorted(["example-model", DEFAULT_MODEL_ID])
        )
        self.assertEqual(
            models.get_service_map(),
            {"example-model": DEFAULT_PROVIDER, DEFAULT_MODEL_ID: DEFAULT_PROVIDER},
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
