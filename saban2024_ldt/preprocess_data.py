import pandas as pd
import random
import string
import numpy as np
import csv
from pathlib import Path

# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
SCRIPT_DIR = Path(__file__).resolve().parent

### Experiment 1 - colour associates-looking pseudowords

#Load the original dataset
df = pd.read_csv(SCRIPT_DIR / "original_data" / "Exp1 - original.csv", sep=';', header=None)

#Remove training trials
df = df[df.iloc[:, 0] != "training"]

#Remove columns irrelevant for this project (e.g., stem frequency, affix, colour)
columns_to_drop = [0,2,3,4,5,6,7,8,9,10,11,12,13,14]
df_cleaned = df.drop(df.columns[columns_to_drop], axis=1)

#Assign names to the columns
df_cleaned.columns=["stimulus", "response", "accuracy", "rt"]

#Remove rows that contain missing values (i.e., the pause between two blocks)
df_cleaned = df_cleaned.dropna()

#Add a trial_order column
df_cleaned["trial_order"] = np.arange(len(df_cleaned)) % 366 + 1

#Add a participant_id column
df_cleaned["participant_id"] = (df_cleaned["trial_order"] == 1).cumsum()

#Reordering columns in the required order
df_final = df_cleaned.loc[:, ['participant_id', 'stimulus', 'response', 'accuracy', 'rt', 'trial_order']]

#"Age" taken from the survey files from psytoolkit

#Remove decimal values from some columns
columns_to_int = ['response', 'accuracy', 'rt']
df_final = df_final.astype({col:'int' for col in columns_to_int})

#Export to csv
df_final.to_csv(SCRIPT_DIR / "processed_data" / "exp1.csv", index=False)


### Experiment 2 - colour words-looking pseudowords

#Load the original dataset
df = pd.read_csv(SCRIPT_DIR / "original_data" / "Exp2 - original.csv", sep=';', header=0)

#Remove columns irrelevant for this project (e.g., stem frequency, affix, colour)
columns_to_drop = ["task", "stem", "affix", "fs", "length", "zipf", "r", "g", "b", "ld", "congruency", "correct", "type"]
df_cleaned = df.drop(columns=columns_to_drop)

#Rename column "participant" to "participant_id"
df_cleaned = df_cleaned.rename(columns={'participant': 'participant_id'})

#Adjust the participant_id (as this will be merged with Experiment 1)
df_cleaned["participant_id"] = df_cleaned["participant_id"] + 27

#Add a trial_order column
df_cleaned["trial_order"] = df_cleaned.groupby("participant_id").cumcount() + 1

#"Age" taken from the survey files from psytoolkit

#Export to csv
df_cleaned.to_csv(SCRIPT_DIR / "processed_data" / "exp2.csv", index=False)

# (removed: a one-off step that rewrote a personal copy of CODEBOOK.csv from
#  semicolon to comma delimiters. The CODEBOOK.csv in this repo is already
#  comma-delimited, so re-running it would misparse and corrupt the file.)
