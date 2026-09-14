#!/usr/bin/env python3
"""Compare a regenerated prompts file against the one committed for a study.

WHY NOT JUST DIFF THE BYTES
---------------------------
22 studies assign their choice-letter mappings with an unseeded RNG (e.g.
`random.sample(string.ascii_lowercase, 2)` per participant). Re-running those
generators produces a file that differs from the committed one on almost every
line, even when nothing is wrong: the same participant gives the same response,
labelled with a different arbitrary letter.

So a byte diff answers the wrong question. What we need to know after editing a
generator is whether the *structure* still matches: same participants, same
number of scored responses, same metadata. This compares that, and only falls
back to byte-identity for studies that seed deterministically.

USAGE
    python3 scripts/harmonization/compare_prompts.py <study> [--new PATH]

By default the committed file is <study>/prompts.jsonl.zip and the regenerated
one is whichever of <study>/prompts.jsonl or the zip is newer. Exit status is 0
when the two are structurally equivalent, 1 otherwise.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MARKER_RE = re.compile(r"<<([^>]*)>>")

# Studies whose generators seed deterministically, so their output should be
# byte-identical across runs. Everything else is compared structurally only.
DETERMINISTIC = {
    "adelman2014_formpriming", "balota2007_LDT", "berzak2025_onestop",
    "devardaetal2024_cloze", "devardaetal2024_rating",
    "devardalamarraetal2025_iconicity", "keuleers2010_DLP1",
    "lally2022_letter_identification", "vergallito2020_ipsn",
}


def load_records(path: Path) -> list[dict]:
    """Read JSONL records from a .jsonl file or a .zip containing one."""
    if path.suffix == ".zip":
        with zipfile.ZipFile(path) as zf:
            name = next(n for n in zf.namelist()
                        if n.endswith(".jsonl") and not n.startswith("__MACOSX"))
            with zf.open(name) as fh:
                return [json.loads(l) for l in io.TextIOWrapper(fh, encoding="utf-8") if l.strip()]
    with path.open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def profile(records: list[dict]) -> dict:
    """Reduce a prompts file to the properties that must not change."""
    pid_key = "participant_id" if records and "participant_id" in records[0] else "participant"
    markers = [len(MARKER_RE.findall(r.get("text", ""))) for r in records]
    keys = Counter()
    for r in records:
        keys.update(r.keys())
    rt_lengths = [len(r["rt"]) for r in records if isinstance(r.get("rt"), list)]
    return {
        "n_records": len(records),
        "participants": {str(r.get(pid_key)) for r in records},
        "n_markers_total": sum(markers),
        "markers_per_record": Counter(markers),
        "keys": keys,
        "experiments": Counter(str(r.get("experiment")) for r in records),
        "n_rt_lists": len(rt_lengths),
        "rt_values_total": sum(rt_lengths),
    }


def compare(study: str, old_path: Path, new_path: Path) -> int:
    old, new = load_records(old_path), load_records(new_path)
    a, b = profile(old), profile(new)
    problems: list[str] = []

    def check(label, x, y):
        mark = "ok  " if x == y else "DIFF"
        if x != y:
            problems.append(f"{label}: committed={x} regenerated={y}")
        print(f"  [{mark}] {label:24} {x}  ->  {y}")

    print(f"\n{study}\n  committed:   {old_path}\n  regenerated: {new_path}\n")
    check("records", a["n_records"], b["n_records"])
    check("participants", len(a["participants"]), len(b["participants"]))
    check("bracketed responses", a["n_markers_total"], b["n_markers_total"])
    check("rt lists", a["n_rt_lists"], b["n_rt_lists"])
    check("rt values total", a["rt_values_total"], b["rt_values_total"])

    missing_p = a["participants"] - b["participants"]
    added_p = b["participants"] - a["participants"]
    if missing_p:
        problems.append(f"participants dropped: {sorted(missing_p)[:5]}")
        print(f"  [DIFF] participants dropped  {len(missing_p)}: {sorted(missing_p)[:5]}")
    if added_p:
        print(f"  [note] participants added    {len(added_p)}: {sorted(added_p)[:5]}")

    # Per-record marker distribution: catches a response silently lost on some
    # trials even when the total happens to match.
    if a["markers_per_record"] != b["markers_per_record"]:
        problems.append("per-record bracket distribution changed")
        print("  [DIFF] per-record bracket distribution changed")

    lost_keys = {k for k in a["keys"] if k not in b["keys"]}
    gained_keys = {k for k in b["keys"] if k not in a["keys"]}
    if lost_keys:
        problems.append(f"metadata fields lost: {sorted(lost_keys)}")
        print(f"  [DIFF] metadata fields lost   {sorted(lost_keys)}")
    if gained_keys:
        print(f"  [note] metadata fields added  {sorted(gained_keys)}")

    if study in DETERMINISTIC:
        identical = old == new
        print(f"  [{'ok  ' if identical else 'DIFF'}] byte-identical (seeded study)")
        if not identical:
            problems.append("seeded study is not reproducing its committed output")

    print()
    if problems:
        print(f"NOT EQUIVALENT ({len(problems)}):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("structurally equivalent")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("study")
    ap.add_argument("--old", type=Path, help="committed file (default <study>/prompts.jsonl.zip)")
    ap.add_argument("--new", type=Path, help="regenerated file (default <study>/prompts.jsonl)")
    args = ap.parse_args()

    d = REPO_ROOT / args.study
    if not d.is_dir():
        print(f"no such study folder: {d}", file=sys.stderr)
        return 2
    old = args.old or d / "prompts.jsonl.zip"
    new = args.new or (d / "prompts.jsonl" if (d / "prompts.jsonl").is_file() else None)
    if new is None:
        print(f"no regenerated file found; run generate_prompts first, or pass --new",
              file=sys.stderr)
        return 2
    for p in (old, new):
        if not p.is_file():
            print(f"missing: {p}", file=sys.stderr)
            return 2
    return compare(args.study, old, new)


if __name__ == "__main__":
    sys.exit(main())
