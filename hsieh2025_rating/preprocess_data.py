# Preprocessing data of hsieh2025_rating

# Load Libraries
import pandas as pd

from pathlib import Path

# Resolve paths from this script's location so the script runs from any
# working directory, on any machine.
SCRIPT_DIR = Path(__file__).resolve().parent

# Read the raw data
df = pd.read_csv(SCRIPT_DIR / "original_data" / "meaningfulness_rating.csv")

# Rename varaibles based on the codebook
rename_map = {
    "participant": "participant_id",
    "item": "stimulus",
    "num": "item_id",
    "rating": "response"
}

df_cleaned = df.rename(columns=rename_map)

# Export the cleaned file
df_cleaned.to_csv(SCRIPT_DIR / "processed_data" / "exp1.csv", index=False)
