# Preprocessing raw data of wang2025_lexicaldecision

# Load Libraries
import pandas as pd
import numpy as np

from pathlib import Path

# Resolve paths from this script's location so the script runs from any
# working directory, on any machine.
SCRIPT_DIR = Path(__file__).resolve().parent

# Read the raw data
df = pd.read_csv(SCRIPT_DIR / "original_data" / "fullresult.csv", encoding="utf-8", index_col=0)

# Create variable "trial_id"
df["trial_id"] = pd.factorize(df["item"])[0] + 1

# Map numeric values to strings in the variable "accuracy" 
df["accuracy"] = df["accuracy"].map({1: "Correct", 0: "Incorrect"})

# Create response based on "lexicality" and "accuracy"
conditions = [
    (df["lexicality"] == "character") & (df["accuracy"] == "Correct"),
    (df["lexicality"] == "pseudocharacter") & (df["accuracy"] == "Incorrect"),
    (df["lexicality"] == "pseudocharacter") & (df["accuracy"] == "Correct"),
    (df["lexicality"] == "character") & (df["accuracy"] == "Incorrect"),
]

choices = ["j", "j", "f", "f"]

# default is an empty string rather than np.nan: numpy >= 2 refuses to find a
# common dtype for string choices and a float default. Blanks are converted
# back to NaN below, so the written CSV is unchanged.
df["response"] = np.select(conditions, choices, default="")
df["response"] = df["response"].replace("", np.nan)

# Rename varaibles based on the codebook
rename_map = {
    "subject": "participant_id",
    "block": "phase_id",
    "item": "stimulus",
    "lexicality": "condition",
    "accuracy": "accuracy",
    "rt": "rt",
    "respons": "response",
    "image_filename": "image_filename",
}

df_cleaned = df.rename(columns=rename_map)

# Make "phase_id" a string variable.
# Cast through the nullable Int64 first: the raw `block` column is float64
# (29 rows are blank), so going straight to "string" renders 0 as "0.0".
df_cleaned["phase_id"] = df_cleaned["phase_id"].astype("Int64").astype("string")

# Column order as committed: the derived trial_id and response sit before
# image_filename rather than being appended after it.
df_cleaned = df_cleaned[[
    "participant_id", "phase_id", "stimulus", "condition", "accuracy",
    "rt", "trial_id", "response", "image_filename",
]]

# Export the cleaned file
df_cleaned.to_csv(SCRIPT_DIR / "processed_data" / "exp1.csv", index=False)