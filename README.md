# Authority Replay Lab

**Can the same one-use authorization commit a second action?**

A small, runnable Python security lab by **Natalia Minkova / Cyber Kimura**.
It checks both the decision and a synthetic state change, then deliberately
breaks enforcement to verify that the replay test notices.

**Standalone educational implementation — not the Kimura engine, not the A02
source release, and not a reproduction of its historical test counts.**
**Synthetic, software-only. No physical robot or aircraft is operated or tested.**
No AI provider, credentials, network, payment API, drone or robot is required.

## Run from a fresh clone (POSIX shell)

Python 3.11+ with its standard-library SQLite and venv modules. No pip dependencies.
There is no `pip install` step: this is a collection of scripts, not an installable
Python package. Git/network access is needed for cloning; the scripts run locally.

```sh
git clone https://github.com/natalia-minkova/authority-replay-lab.git
cd authority-replay-lab
python3 -m venv .venv
. .venv/bin/activate
python3 replay_lab.py
python3 -m unittest -v
python3 check_mutation.py
```

If `python3 -m venv` reports that venv/ensurepip is unavailable, install your
operating system's venv support for that Python version first. The commands above
use a POSIX shell; Windows activation syntax is different.

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

## Recorded reproduction

[Unsigned clean-run record](evidence/clean-run-2026-11-03.md): exact tested commit,
Python/SQLite versions, commands, observed output summary and limitations.
[GitHub Actions](https://github.com/natalia-minkova/authority-replay-lab/actions)
runs the README commands in fresh venvs on Python 3.11 and 3.12 on Ubuntu.
Check the individual run for its status; configured checks alone are not proof
that a run passed.

## What a reviewer can inspect

| Scenario | Required outcome |
| --- | --- |
| Exact authorised request | One simulated effect |
| Same grant reused | Denied; effect count remains one |
| Database reopened | Consumed state remains enforced |
| Eight concurrent attempts | One allowed; seven rejected; one effect |
| Different actor, target or amount | Rejected; no simulated effect |
| Wrong actor followed by valid request | Valid grant remains usable |
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

### Evidence integrity

This lab produces local, unsigned output. It does **not** implement a tamper-evident
or authenticated evidence capsule. A checksum alongside a file is not proof of its
authenticity. Any separate signed capsule must have its verification key bound to
the claimed signer through a trusted channel before it can be treated as
authenticated evidence. Even an authenticated signature does not prove a claimed
physical event occurred.

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
