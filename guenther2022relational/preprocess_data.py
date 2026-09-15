import os
from pathlib import Path
import pandas as pd


def ensure_processed_dir(base_dir: Path) -> Path:
    processed_dir = base_dir / "processed_data"
    processed_dir.mkdir(exist_ok=True)
    return processed_dir


def write_codebook(base_dir: Path) -> None:
    codebook_path = base_dir / "CODEBOOK.csv"
    if codebook_path.exists():
        return
    rows = [
        {"column_name": "participant_id", "description": "Anonymized participant ID"},
        {"column_name": "age", "description": "Participant age in years (from 'age')"},
        {"column_name": "trial_order", "description": "Trial order index (factorized from raw trial_order)"},
        {"column_name": "stimulus", "description": "Stimulus string (from 'stim')"},
        {"column_name": "response", "description": "Participant response (from 'responses')"},
        {"column_name": "rt", "description": "Time taken by the participant to respond, in milliseconds"},
    ]
    pd.DataFrame(rows).to_csv(codebook_path, index=False)


def preprocess(base_dir: Path) -> None:
    original_path = base_dir / "original_data" / "relational_entropy_novelcomp_raw.csv"
    processed_dir = ensure_processed_dir(base_dir)
    write_codebook(base_dir)

    df = pd.read_csv(original_path)

    # Rename / create canonical columns
    df = df.rename(columns={"responses": "response"})
    if "stim" in df.columns:
        df["stimulus"] = df["stim"]

    # Factorize trial_order to integers starting at 1
    # The raw export names this column trial_id; the corpus name for a
    # per-participant position is trial_order.
    if "trial_id" in df.columns:
        df["trial_order"] = pd.factorize(df["trial_id"])[0] + 1

    # turn age to float
    df["age"] = df["age"].astype(float)
    
    # Select and sort
    cols = ["participant_id", "age", "trial_order", "stimulus", "response", "rt"]
    df_out = df.loc[:, [c for c in cols if c in df.columns]].copy()
    df_out = df_out.sort_values(by=[c for c in ["participant_id", "trial_order"] if c in df_out.columns])

    # Write
    out_path = processed_dir / "exp1.csv"
    df_out["rt_measure"] = "keypress"
    df_out.to_csv(out_path, index=False)


if __name__ == "__main__":
    preprocess(Path(__file__).parent.resolve())


