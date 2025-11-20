from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime
from importlib import import_module
from pathlib import Path

from pixelforge_ops import utils


class UtilsExtendedTests(unittest.TestCase):
    def test_utcnow_text_ends_with_z(self) -> None:
        self.assertTrue(utils.utcnow_text().endswith("Z"))

    def test_utcnow_text_has_no_microseconds(self) -> None:
        self.assertNotIn(".", utils.utcnow_text())

    def test_utcnow_text_is_iso_parseable(self) -> None:
        value = utils.utcnow_text().replace("Z", "+00:00")
        self.assertIsInstance(datetime.fromisoformat(value), datetime)

    def test_stable_json_sorts_keys(self) -> None:
        text = utils.stable_json({"b": 2, "a": 1})
        self.assertLess(text.index('"a"'), text.index('"b"'))

    def test_stable_json_ends_with_newline(self) -> None:
        self.assertTrue(utils.stable_json({"a": 1}).endswith("\n"))

    def test_json_digest_is_stable_for_same_payload(self) -> None:
        self.assertEqual(utils.json_digest({"a": 1}), utils.json_digest({"a": 1}))

    def test_json_digest_changes_for_different_payloads(self) -> None:
        self.assertNotEqual(utils.json_digest({"a": 1}), utils.json_digest({"a": 2}))

    def test_read_json_round_trips_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.json"
            path.write_text(json.dumps({"a": 1}), encoding="utf-8")
            self.assertEqual(utils.read_json(path), {"a": 1})

    def test_read_jsonl_reads_multiple_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.jsonl"
            path.write_text('{"a": 1}\n{"b": 2}\n', encoding="utf-8")
            self.assertEqual(utils.read_jsonl(path), [{"a": 1}, {"b": 2}])

    def test_write_json_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "payload.json"
            utils.write_json(path, {"a": 1})
            self.assertTrue(path.exists())

    def test_write_json_sorts_keys_in_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.json"
            utils.write_json(path, {"b": 2, "a": 1})
            text = path.read_text(encoding="utf-8")
            self.assertLess(text.index('"a"'), text.index('"b"'))

    def test_write_jsonl_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "payload.jsonl"
            utils.write_jsonl(path, [{"a": 1}])
            self.assertTrue(path.exists())

    def test_write_jsonl_ends_with_newline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.jsonl"
            utils.write_jsonl(path, [{"a": 1}])
            self.assertTrue(path.read_text(encoding="utf-8").endswith("\n"))

    def test_slugify_lowercases_words(self) -> None:
        self.assertEqual(utils.slugify("Finance Ops"), "finance-ops")

    def test_slugify_collapses_repeated_delimiters(self) -> None:
        self.assertEqual(utils.slugify("Finance --- Ops"), "finance-ops")

    def test_slugify_falls_back_to_unknown_for_blank_text(self) -> None:
        self.assertEqual(utils.slugify("   "), "unknown")

    def test_slugify_strips_leading_and_trailing_dashes(self) -> None:
        self.assertEqual(utils.slugify("--Finance Ops--"), "finance-ops")

    def test_ensure_dir_returns_original_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested"
            self.assertEqual(utils.ensure_dir(path), path)

    def test_ensure_dir_creates_nested_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "leaf"
            utils.ensure_dir(path)
            self.assertTrue(path.exists())

    def test_relative_files_returns_sorted_relative_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "b.txt").write_text("b", encoding="utf-8")
            (root / "nested").mkdir()
            (root / "nested" / "a.txt").write_text("a", encoding="utf-8")
            self.assertEqual(utils.relative_files(root), ["b.txt", "nested/a.txt"])

    def test_relative_files_skips_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nested").mkdir()
            self.assertEqual(utils.relative_files(root), [])

    def test_env_flag_returns_false_default_when_missing(self) -> None:
        self.assertFalse(utils.env_flag("ASSESSMENT_OPS_MISSING_ENV_FLAG"))

    def test_env_flag_returns_true_default_when_missing(self) -> None:
        self.assertTrue(utils.env_flag("ASSESSMENT_OPS_MISSING_ENV_FLAG_TWO", default=True))

    def test_env_flag_treats_one_as_true(self) -> None:
        os.environ["ASSESSMENT_OPS_ENV_FLAG"] = "1"
        try:
            self.assertTrue(utils.env_flag("ASSESSMENT_OPS_ENV_FLAG"))
        finally:
            os.environ.pop("ASSESSMENT_OPS_ENV_FLAG", None)

    def test_env_flag_treats_true_as_true(self) -> None:
        os.environ["ASSESSMENT_OPS_ENV_FLAG"] = "true"
        try:
            self.assertTrue(utils.env_flag("ASSESSMENT_OPS_ENV_FLAG"))
        finally:
            os.environ.pop("ASSESSMENT_OPS_ENV_FLAG", None)

    def test_env_flag_treats_yes_as_true(self) -> None:
        os.environ["ASSESSMENT_OPS_ENV_FLAG"] = "yes"
        try:
            self.assertTrue(utils.env_flag("ASSESSMENT_OPS_ENV_FLAG"))
        finally:
            os.environ.pop("ASSESSMENT_OPS_ENV_FLAG", None)

    def test_env_flag_treats_on_as_true(self) -> None:
        os.environ["ASSESSMENT_OPS_ENV_FLAG"] = "on"
        try:
            self.assertTrue(utils.env_flag("ASSESSMENT_OPS_ENV_FLAG"))
        finally:
            os.environ.pop("ASSESSMENT_OPS_ENV_FLAG", None)

    def test_env_flag_treats_off_as_false(self) -> None:
        os.environ["ASSESSMENT_OPS_ENV_FLAG"] = "off"
        try:
            self.assertFalse(utils.env_flag("ASSESSMENT_OPS_ENV_FLAG"))
        finally:
            os.environ.pop("ASSESSMENT_OPS_ENV_FLAG", None)

    def test_env_flag_treats_zero_as_false(self) -> None:
        os.environ["ASSESSMENT_OPS_ENV_FLAG"] = "0"
        try:
            self.assertFalse(utils.env_flag("ASSESSMENT_OPS_ENV_FLAG"))
        finally:
            os.environ.pop("ASSESSMENT_OPS_ENV_FLAG", None)

    def test_package_shim_can_import_catalog_module(self) -> None:
        module = import_module("pixelforge_ops.catalog")
        self.assertTrue(hasattr(module, "load_bundle"))

    def test_package_shim_points_at_src_tree(self) -> None:
        package = import_module("pixelforge_ops")
        self.assertTrue(any("src" in item for item in package.__path__))


