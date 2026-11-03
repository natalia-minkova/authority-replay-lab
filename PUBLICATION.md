# Public demonstration boundary

This is a fresh, deliberately limited implementation of a generic single-use
state-transition example. It is not extracted from the private Kimura repository.

## Included

- Human-readable Python implementation and synthetic fixtures.
- A bounded contract: exact actor/target/amount and one committed local effect.
- Positive, negative, persistence, concurrency and rollback tests.
- One explicit mutation used to test the replay assertion.
- Run instructions, expected output and explicit trust assumptions.

## Excluded

- Proprietary fuzzers, payload libraries and scenario-generation strategies.
- Internal assessment orchestration, scoring and commercial adapters.
- Private schemas, customer logs, client names, credentials and signing keys.
- Private repository history or historical artifacts repackaged as new evidence.

## Interpreting the result

A successful run establishes only the assertions executed against this example
on that runtime. The result is not an independent audit or validation of A02,
a real agent, a flight controller, a physical robot or a customer's system.

For review, retain the public commit SHA, Python/SQLite versions and terminal
output. Run from that commit in a fresh directory. No claim is made that a file
hash or a passing suite by itself proves an external event occurred.
