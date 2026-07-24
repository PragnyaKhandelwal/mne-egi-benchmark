"""Compare benchmark results from two different MNE branches."""

import json
import sys
from pathlib import Path

import numpy as np
import mne


def load_meta(path):
    return json.loads(Path(path).read_text())


def compare(meta_path_1, meta_path_2):
    m1 = load_meta(meta_path_1)
    m2 = load_meta(meta_path_2)

    print(f"\n{'='*60}")
    print(f"  A: {m1['branch']}@{m1['commit']}  (mne {m1['mne_version']})")
    print(f"  B: {m2['branch']}@{m2['commit']}  (mne {m2['mne_version']})")
    print(f"{'='*60}\n")

    scalar_checks = ["n_channels", "sfreq", "duration_s", "n_annotations"]
    for key in scalar_checks:
        v1, v2 = m1[key], m2[key]
        mark = "PASS" if v1 == v2 else "FAIL"
        print(f"  [{mark}] {key}: {v1} vs {v2}")

    ch1, ch2 = set(m1["ch_names"]), set(m2["ch_names"])
    if ch1 == ch2:
        print(f"  [PASS] ch_names: identical ({len(ch1)} channels)")
    else:
        print(f"  [FAIL] ch_names: only in A={ch1 - ch2}  only in B={ch2 - ch1}")

    ann1 = set(m1["annotation_descriptions"])
    ann2 = set(m2["annotation_descriptions"])
    if ann1 == ann2:
        print(f"  [PASS] annotation types: identical ({sorted(ann1)})")
    else:
        print(f"  [FAIL] annotation types: only in A={ann1 - ann2}  only in B={ann2 - ann1}")

    dt = m2["read_time_s"] - m1["read_time_s"]
    print(f"\n  read_time: {m1['read_time_s']}s (A)  vs  {m2['read_time_s']}s (B)  ({dt:+.3f}s)")

    fif1 = Path(meta_path_1).parent / Path(meta_path_1).name.replace("_meta.json", "_raw.fif")
    fif2 = Path(meta_path_2).parent / Path(meta_path_2).name.replace("_meta.json", "_raw.fif")
    if fif1.exists() and fif2.exists():
        print("\n  Loading FIF files for data comparison...")
        raw1 = mne.io.read_raw_fif(fif1, preload=True, verbose=False)
        raw2 = mne.io.read_raw_fif(fif2, preload=True, verbose=False)
        d1, d2 = raw1.get_data(), raw2.get_data()
        if d1.shape == d2.shape:
            max_diff = np.max(np.abs(d1 - d2))
            allclose = np.allclose(d1, d2, atol=1e-12)
            mark = "PASS" if allclose else "FAIL"
            print(f"  [{mark}] raw data: shape={d1.shape}  max_abs_diff={max_diff:.2e}")
        else:
            print(f"  [FAIL] raw data shapes differ: {d1.shape} vs {d2.shape}")
    else:
        print("\n  (FIF files not found locally — skipping data comparison)")

    print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare.py results/A_meta.json results/B_meta.json")
        sys.exit(1)
    compare(sys.argv[1], sys.argv[2])
