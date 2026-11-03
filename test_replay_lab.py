import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from replay_lab import Gate


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'lab.sqlite'
        self.gate = Gate(self.path)
        self.args = ('grant-1', 'alice', 'account-a', 5000)
        self.gate.issue(*self.args)

    def test_allowed_action_creates_one_effect(self):
        self.assertEqual(self.gate.exercise(*self.args), 'ALLOWED')
        self.assertEqual(self.gate.effect_count(), 1)

    def test_replay_has_no_second_effect(self):
        self.gate.exercise(*self.args)
        self.assertEqual(self.gate.exercise(*self.args), 'AUTHORITY_ALREADY_CONSUMED')
        self.assertEqual(self.gate.effect_count(), 1)

    def test_consumption_survives_reopening(self):
        self.gate.exercise(*self.args)
        reopened = Gate(self.path)
        self.assertEqual(reopened.exercise(*self.args), 'AUTHORITY_ALREADY_CONSUMED')
        self.assertEqual(reopened.effect_count(), 1)

    def test_wrong_actor_does_not_consume_grant(self):
        self.assertEqual(self.gate.exercise('grant-1', 'bob', 'account-a', 5000), 'SCOPE_MISMATCH')
        self.assertEqual(self.gate.effect_count(), 0)
        self.assertEqual(self.gate.exercise(*self.args), 'ALLOWED')

    def test_wrong_target_is_denied(self):
        self.assertEqual(self.gate.exercise('grant-1', 'alice', 'account-b', 5000), 'SCOPE_MISMATCH')
        self.assertEqual(self.gate.effect_count(), 0)

    def test_amount_escalation_is_denied(self):
        self.assertEqual(self.gate.exercise('grant-1', 'alice', 'account-a', 50000), 'SCOPE_MISMATCH')
        self.assertEqual(self.gate.effect_count(), 0)

    def test_unknown_authority_is_denied(self):
        self.assertEqual(self.gate.exercise('unknown', 'alice', 'account-a', 5000), 'UNKNOWN_AUTHORITY')
        self.assertEqual(self.gate.effect_count(), 0)

    def test_invalid_amounts_are_denied(self):
        for amount in (True, 0, -1, 5000.0, '5000'):
            with self.subTest(amount=amount):
                self.assertEqual(self.gate.exercise('grant-1', 'alice', 'account-a', amount), 'INVALID_AMOUNT')
        self.assertEqual(self.gate.effect_count(), 0)

    def test_duplicate_issue_cannot_reset_consumption(self):
        self.gate.exercise(*self.args)
        with self.assertRaises(sqlite3.IntegrityError):
            self.gate.issue(*self.args)
        self.assertEqual(self.gate.exercise(*self.args), 'AUTHORITY_ALREADY_CONSUMED')

    def test_concurrent_replays_commit_only_one_effect(self):
        barrier = threading.Barrier(8)
        def attempt(_):
            barrier.wait(timeout=10)
            return self.gate.exercise(*self.args)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(attempt, range(8)))
        self.assertEqual(results.count('ALLOWED'), 1)
        self.assertEqual(results.count('AUTHORITY_ALREADY_CONSUMED'), 7)
        self.assertEqual(self.gate.effect_count(), 1)

    def test_effect_failure_rolls_back_consumption(self):
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TRIGGER fail_effect BEFORE INSERT ON effects BEGIN SELECT RAISE(ABORT, 'injected failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.gate.exercise(*self.args)
        self.assertEqual(self.gate.effect_count(), 0)
        with sqlite3.connect(self.path) as db:
            db.execute('DROP TRIGGER fail_effect')
        self.assertEqual(self.gate.exercise(*self.args), 'ALLOWED')
        self.assertEqual(self.gate.effect_count(), 1)


if __name__ == '__main__':
    unittest.main()
