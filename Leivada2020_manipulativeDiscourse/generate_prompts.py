import pandas as pd
import json
from pathlib import Path

# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
SCRIPT_DIR = Path(__file__).resolve().parent

df1 = pd.read_csv(SCRIPT_DIR / "processed_data" / "exp1.csv", quotechar='"', dtype=str)
df2 = pd.read_csv(SCRIPT_DIR / "processed_data" / "exp2.csv", quotechar='"', dtype=str)

# Assign experiment labels
df1['experiment'] = 'exp1'
df2['experiment'] = 'exp2'


# Combine them into a single DataFrame
df = pd.concat([df1, df2], ignore_index=True)

# Group by participant (if multiple rows per participant)
grouped = df.groupby('participant_id')

jsonl_lines = []

for participant_id, group in grouped:
    # Start building the text field
    text_parts = [
        "Instruction:\nRate how correct each sentence sounds.\nOptions: correct / neither correct nor wrong / wrong.\n"
    ]

    # Enumerate sentences
    for i, row in enumerate(group.itertuples(), start=1):
        # Capitalize the response to match format
        response = str(row.response).capitalize()
        text_parts.append(
            f"Sentence {i}:\n{row.stimulus}\nYour response: <<{response}>>"
        )

    # Combine all sentences into one string
    text_field = "\n\n".join(text_parts)

    # Build JSON object
    json_obj = {
        # "participant_id" is the field name the repository requires; this wrote
        # "participant", which silently breaks anything reading the standard key.
        "participant_id": participant_id,
        "text": text_field,
        "experiment": group['experiment'].iloc[0],  # automatically pick exp1 or exp2
        "age": int(group['age'].iloc[0]),          # convert numpy int to Python int
        # Per-trial reaction times in ms, in the same order as the trials above.
        "rt": group['rt'].tolist(),
    }
    # Carry through whatever participant metadata this experiment recorded.
    for _col in ("gender", "education", "handedness", "country_of_residence"):
        if _col in group.columns and pd.notna(group[_col].iloc[0]):
            json_obj[_col] = group[_col].iloc[0]

    # Convert to JSON string (single line)
    jsonl_lines.append(json.dumps(json_obj, ensure_ascii=False))

# Write to JSONL file
jsonl_path = SCRIPT_DIR / "prompts.jsonl"
with open(jsonl_path, "w", encoding="utf-8") as f:
    for line in jsonl_lines:
        f.write(line + "\n")

# Package the deliverable: the layout requires <study>/prompts.jsonl.zip with a
# single entry named prompts.jsonl. This script previously wrote only the loose
# .jsonl, so the committed archive had to be built by hand.
import zipfile
with zipfile.ZipFile(SCRIPT_DIR / "prompts.jsonl.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(jsonl_path, "prompts.jsonl")
jsonl_path.unlink()

print("JSONL file created successfully from both CSVs!")