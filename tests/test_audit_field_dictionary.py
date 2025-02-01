from __future__ import annotations

import unittest

from engineering_challenge.auditpack import field_dictionary


class AuditFieldDictionaryTests(unittest.TestCase):
    def test_field_definition_returns_row(self) -> None:
        row = field_dictionary.field_definition("audit_field_001")
        self.assertEqual(row["field"], "audit_field_001")

    def test_required_fields_are_non_empty(self) -> None:
        self.assertTrue(field_dictionary.required_fields())

    def test_fields_for_source_filters_rows(self) -> None:
        rows = field_dictionary.fields_for_source("bundle")
        self.assertTrue(rows)
