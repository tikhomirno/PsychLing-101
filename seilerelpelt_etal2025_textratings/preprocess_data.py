#!/usr/bin/env python3
"""Preprocessing for Seiler, Elpelt et al. (2025) text ratings.

Reconstructed: the file committed with the submission was 0 bytes, so the study
shipped with no preprocessing step at all. The transformation was recovered by
comparing original_data/data_table_1.csv against the committed
processed_data/exp1.csv -- the two are byte-identical, so the contributor had
already standardized their export to the CODEBOOK vocabulary before submitting
and the step is a validated copy rather than a transformation.

Rather than copying blindly, this verifies that the raw file really does carry the
canonical columns before writing, so a future change to the raw export fails here
instead of silently producing a non-conforming processed_data.
"""
from pathlib import Path

import pandas as pd

# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
SCRIPT_DIR = Path(__file__).resolve().parent
ORIGINAL_DATA_DIR = SCRIPT_DIR / "original_data"
PROCESSED_DATA_DIR = SCRIPT_DIR / "processed_data"

SOURCE = ORIGINAL_DATA_DIR / "data_table_1.csv"

# The columns processed_data/exp1.csv is expected to carry, in order.
EXPECTED_COLUMNS = [
    "participant_id",
    "age",
    "gender",
    "clinical_diagnoses",
    "country_of_residence",
    "trial_id",
    "stimulus",
    "condition",
    "response",
]


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing required input: {SOURCE}")

    df = pd.read_csv(SOURCE)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise SystemExit(
            f"{SOURCE.name} does not carry the expected columns: {missing}\n"
            "The raw export previously matched the CODEBOOK vocabulary exactly. If it "
            "has changed, this script needs a real transformation step rather than a copy."
        )

    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if extra:
        print(f"  note: dropping columns not in the codebook: {extra}")
    df = df[EXPECTED_COLUMNS]

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DATA_DIR / "exp1.csv"
    df.to_csv(out, index=False)

    print(f"Wrote {out}")
    print(f"  rows        : {len(df)}")
    print(f"  participants: {df['participant_id'].nunique()}")
    print(f"  stimuli     : {df['stimulus'].nunique()}")


if __name__ == "__main__":
    main()
