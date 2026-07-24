"""Benchmark MNE EGI MFF reader: read an MFF file, save to FIF, record metadata."""

import json
import subprocess
import time
from pathlib import Path

import mne
import pooch

RESULTS_DIR = Path(__file__).parent / "results"
DATA_DIR = Path(__file__).parent / "data"

# OSF file registry for osf.io/d245g — fill in file IDs + hashes after checking the project
OSF_FILES = {
    # "filename.mff": ("https://osf.io/<file_id>/download", "sha256:<hash>"),
}


def get_mne_git_info():
    mne_root = Path(mne.__file__).parent.parent
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=mne_root, text=True, stderr=subprocess.DEVNULL,
        ).strip()
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=mne_root, text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        branch, commit = "unknown", "unknown"
    return branch, commit


def download_data():
    DATA_DIR.mkdir(exist_ok=True)
    paths = []
    for fname, (url, known_hash) in OSF_FILES.items():
        path = pooch.retrieve(url=url, known_hash=known_hash, fname=fname, path=DATA_DIR)
        paths.append(Path(path))
    return paths


def benchmark(mff_path):
    RESULTS_DIR.mkdir(exist_ok=True)
    branch, commit = get_mne_git_info()
    stem = f"{branch}_{commit}"

    print(f"\nReading: {mff_path.name}")
    t0 = time.perf_counter()
    raw = mne.io.read_raw_egi(mff_path, preload=True, verbose=False)
    read_time = round(time.perf_counter() - t0, 4)

    fif_path = RESULTS_DIR / f"{stem}_raw.fif"
    raw.save(fif_path, overwrite=True, verbose=False)

    meta = {
        "branch": branch,
        "commit": commit,
        "mne_version": mne.__version__,
        "source_file": mff_path.name,
        "read_time_s": read_time,
        "n_channels": raw.info["nchan"],
        "sfreq": raw.info["sfreq"],
        "duration_s": round(raw.times[-1], 3),
        "n_annotations": len(raw.annotations),
        "annotation_descriptions": sorted(set(raw.annotations.description)),
        "ch_names": raw.ch_names,
    }
    json_path = RESULTS_DIR / f"{stem}_meta.json"
    json_path.write_text(json.dumps(meta, indent=2))

    print(f"  branch={branch} | commit={commit} | mne={mne.__version__}")
    print(f"  read_time={read_time}s | channels={raw.info['nchan']} | sfreq={raw.info['sfreq']}Hz")
    print(f"  duration={raw.times[-1]:.1f}s | annotations={len(raw.annotations)}")
    print(f"  saved -> {fif_path.name}, {json_path.name}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark MNE EGI MFF reader.")
    parser.add_argument("paths", nargs="*", help="Local .mff paths (bypasses download)")
    args = parser.parse_args()

    if args.paths:
        for p in args.paths:
            benchmark(Path(p))
    else:
        paths = download_data()
        if not paths:
            print("No local paths given and OSF_FILES registry is empty.")
            print("Usage: python benchmark.py path/to/file.mff")
        else:
            for p in paths:
                benchmark(p)
