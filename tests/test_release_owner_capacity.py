from __future__ import annotations

import unittest

from engineering_challenge.release_ops import owner_capacity


class OwnerCapacityTests(unittest.TestCase):
    def test_week_rows_return_many_weeks(self) -> None:
        self.assertGreaterEqual(len(owner_capacity.week_rows()), 20)

    def test_capacity_for_week_returns_integer(self) -> None:
        first_week = owner_capacity.week_rows()[0]["week_start"]
        self.assertGreater(owner_capacity.capacity_for_week("finance_ops", first_week), 0)

    def test_blackout_owners_returns_list(self) -> None:
        first_week = owner_capacity.week_rows()[0]["week_start"]
        self.assertIsInstance(owner_capacity.blackout_owners(first_week), list)
