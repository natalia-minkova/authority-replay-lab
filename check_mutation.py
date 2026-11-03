"""Run one targeted mutation in a temporary copy; never edit the working tree."""
import pathlib
import shutil
import subprocess
import sys
import tempfile

root = pathlib.Path(__file__).resolve().parent
source = (root / 'replay_lab.py').read_text()
needle = "if row[3]:  # MUTATION_POINT: removing this guard must break replay tests"
if source.count(needle) != 1:
    raise SystemExit('Mutation point missing or ambiguous')
# Require an unchanged baseline to pass first.
baseline = subprocess.run([sys.executable, '-m', 'unittest', '-q'], cwd=root)
if baseline.returncode:
    raise SystemExit('Baseline failed; mutation result is not valid')
with tempfile.TemporaryDirectory() as folder:
    mutant = pathlib.Path(folder)
    (mutant / 'replay_lab.py').write_text(source.replace(needle, 'if False:  # deliberately broken guard'))
    shutil.copyfile(root / 'test_replay_lab.py', mutant / 'test_replay_lab.py')
    result = subprocess.run([sys.executable, '-m', 'unittest',
                             'test_replay_lab.ReplayTests.test_replay_has_no_second_effect'],
                            cwd=mutant, text=True, capture_output=True)
    # An import error or crash does not count as detection of the missing guard.
    if result.returncode != 1 or 'FAIL:' not in result.stderr or 'AssertionError:' not in result.stderr or 'ERROR:' in result.stderr:
        print(result.stderr)
        raise SystemExit('Mutation was not detected by the expected assertion')
print('MUTATION_DETECTED: replay test rejected the missing single-use guard')
