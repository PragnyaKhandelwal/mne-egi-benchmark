# mne-egi-benchmark

Benchmarking and parity testing for the MNE-Python EGI MFF reader (GSoC 2026 — [meta-issue #13926](https://github.com/mne-tools/mne-python/issues/13926)).

Compares the legacy EGI reader against the new `mffpy`-based backend by reading the same MFF file on different branches and diffing the output.

## Setup

```bash
python -m venv .venv
# activate venv, then install local mne-python in editable mode:
pip install -e path/to/mne-python
```

## Usage

**1. Run benchmark on current branch:**
```bash
python benchmark.py path/to/file.mff
```
Saves `results/<branch>_<commit>_raw.fif` and `results/<branch>_<commit>_meta.json`.

**2. Switch branch and run again:**
```bash
# in mne-python repo
git checkout main
# back here
python benchmark.py path/to/file.mff
```

**3. Compare results:**
```bash
python compare.py results/branch_a_meta.json results/branch_b_meta.json
```

## What gets recorded

- Branch name and commit hash
- MNE version
- Read time (seconds)
- Channel count, sampling frequency, duration
- Number and types of annotations
- Channel names
- Raw data saved as FIF for numerical comparison
