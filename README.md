# Authority Replay Lab

**Can the same one-use authorization commit a second action?**

A small, runnable Python security lab by **Natalia Minkova / Cyber Kimura**.
It checks both the decision and a synthetic state change, then deliberately
breaks enforcement to verify that the replay test notices.

**Standalone educational implementation — not the Kimura engine, not the A02
source release, and not a reproduction of its historical test counts.**
No AI provider, credentials, network, payment API, drone or robot is required.

## Run in one minute

Python 3.11+ with its standard-library SQLite module. No pip dependencies.

```sh
git clone https://github.com/natalia-minkova/authority-replay-lab.git
cd authority-replay-lab
python3 replay_lab.py
python3 -m unittest -v
python3 check_mutation.py
```

The demo creates a temporary local database and removes it on exit. Expected output:

```json
{
  "scope": "SYNTHETIC_LOCAL_SQLITE",
  "first": "ALLOWED",
  "replay": "AUTHORITY_ALREADY_CONSUMED",
  "simulated_effect_count": 1
}
```

The suite currently contains **11 tests**, including five invalid-amount subcases.
The targeted mutation check must finish with:

```text
MUTATION_DETECTED: replay test rejected the missing single-use guard
```

It first checks the unmodified baseline, then removes exactly one guard in a
temporary copy. An import error or crash does not count as a detected mutation.
This is one targeted mutation, not a general mutation score or proprietary fuzzer.

## What a reviewer can inspect

| Scenario | Required outcome |
| --- | --- |
| Exact authorised request | One simulated effect |
| Same grant reused | Denied; effect count remains one |
| Database reopened | Consumed state remains enforced |
| Eight concurrent attempts | One allowed; seven rejected; one effect |
| Different actor, target or amount | Rejected without consuming the valid grant |
| Duplicate issuance | Cannot reset a consumed grant |
| Effect insertion fails | Transaction rolls back consumption and effect |
| Replay guard deliberately removed | Replay assertion fails |

Start with [the implementation](replay_lab.py), then [the tests](test_replay_lab.py)
and [the mutation check](check_mutation.py). Tests inspect stored synthetic effects,
not just the gate's return string.

## Trust model and limits

- The issuer, Python process, SQLite implementation and local storage are trusted.
  Actor strings are caller-supplied test inputs, **not authenticated identities**.
- Consumption and the mock effect are committed in the **same SQLite transaction**.
  This does not establish exactly-once execution across external services or hardware.
- The concurrency test uses independent SQLite connections from eight local threads.
  It is not a distributed-systems or crash/power-loss qualification.
- Anyone with database write access can reset or rewrite the state. No host-root,
  rollback protection, cryptographic authorization, signatures or external custody
  is implemented here. Grant IDs are fixture identifiers, not secret credentials.
- No real money moves. No robot moves. This lab is not a production authorization
  component, a customer assessment or a guarantee for untested inputs.

## Related work

[Authority Replay A02 case-study narrative](https://cyberkimura.com/case-study/)
explores the related single-use-authority question. This new lab illustrates the
principle independently; running it does **not** verify the historical A02 run.

[Cyber Kimura](https://cyberkimura.com) ·
[GitHub profile](https://github.com/natalia-minkova) ·
[Contact](mailto:security@cyberkimura.com)

## Publication boundary

This repository contains newly written educational code and synthetic fixtures.
No private engine source, fuzzing corpus, client artifacts, credentials or private
Git history has been imported. See [PUBLICATION.md](PUBLICATION.md).

Copyright 2026 Natalia Minkova. No broad open-source license is granted by this
publication. Contact the author for reuse permission beyond applicable rights.
