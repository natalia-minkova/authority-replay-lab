"""Standalone synthetic teaching example. Not the Kimura assessment engine."""
import json
import sqlite3
import tempfile
from pathlib import Path


class Gate:
    """Trusted local issuer/store; no network authentication or external effects."""

    def __init__(self, path):
        self.path = str(path)
        with self._connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS grants (
                    id TEXT PRIMARY KEY, actor TEXT NOT NULL,
                    target TEXT NOT NULL, amount INTEGER NOT NULL,
                    consumed INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS effects (
                    sequence INTEGER PRIMARY KEY, grant_id TEXT NOT NULL,
                    amount INTEGER NOT NULL);
            ''')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def issue(self, grant_id, actor, target, amount):
        if type(amount) is not int or amount <= 0:
            raise ValueError('amount must be a positive integer in synthetic cents')
        with self._connect() as db:
            db.execute('INSERT INTO grants(id, actor, target, amount) VALUES(?,?,?,?)',
                       (grant_id, actor, target, amount))

    def exercise(self, grant_id, actor, target, amount):
        if type(amount) is not int or amount <= 0:
            return 'INVALID_AMOUNT'
        with self._connect() as db:
            # Consumption and the simulated effect share ONE SQLite transaction.
            # This does not extend to external payment or robot APIs.
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT actor,target,amount,consumed FROM grants WHERE id=?',
                             (grant_id,)).fetchone()
            if row is None:
                return 'UNKNOWN_AUTHORITY'
            if row[:3] != (actor, target, amount):
                return 'SCOPE_MISMATCH'
            if row[3]:  # MUTATION_POINT: removing this guard must break replay tests
                return 'AUTHORITY_ALREADY_CONSUMED'
            db.execute('UPDATE grants SET consumed=1 WHERE id=?', (grant_id,))
            db.execute('INSERT INTO effects(grant_id,amount) VALUES(?,?)', (grant_id, amount))
        return 'ALLOWED'

    def effect_count(self):
        with self._connect() as db:
            return db.execute('SELECT COUNT(*) FROM effects').fetchone()[0]


def demo():
    with tempfile.TemporaryDirectory() as folder:
        gate = Gate(Path(folder) / 'synthetic.sqlite')
        gate.issue('demo-grant', 'demo-actor', 'demo-account', 5000)
        first = gate.exercise('demo-grant', 'demo-actor', 'demo-account', 5000)
        replay = gate.exercise('demo-grant', 'demo-actor', 'demo-account', 5000)
        print(json.dumps({'scope': 'SYNTHETIC_LOCAL_SQLITE', 'first': first,
                          'replay': replay, 'simulated_effect_count': gate.effect_count()},
                         indent=2))


if __name__ == '__main__':
    demo()
