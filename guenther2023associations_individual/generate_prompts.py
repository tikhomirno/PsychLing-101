import pandas as pd
import jsonlines
import sys
from pathlib import Path
import zipfile

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent / "scripts" / "harmonization")
)
from bracket_safety import join_consecutive, sanitize_bracket_response  # noqa: E402

# load data
base_dir = Path(__file__).parent.resolve()
exp = pd.read_csv(base_dir / "processed_data" / "exp1.csv")

response_cols = [f"response{i}" for i in range(1, 11)]

# Keep the ten associations separate rather than joining them into one string.
# Each is its own response and needs its own <<>> span: comma-joined inside a
# single bracket, the training collator scores all ten as one item, and the ">>"
# before each comma is not found at all.
# Built with a list comprehension, not .apply(axis=1), because an apply that
# returns equal-length lists expands into a DataFrame instead of a column.
exp["response"] = [
    [x for x in row if pd.notna(x)]
    for row in exp[response_cols].itertuples(index=False)
]

# Define number of participants and trials
participants_exp = exp['participant_id'].unique()
trials_exp = range(exp['trial_order'].max() + 1)

# define initial prompt
instruction = 'On the top of the screen a word will appear. Enter the first 10 words that come to mind when reading this word.\n'\
    'Please enter 10 different words for each word presented to you.\n'\
    'Please take this task seriously, and enter actual words. We kindly ask you to ensure that these words are spelled correctly.\n'\
    'Some hints\n'\
    'Only give associations to the word on top of the screen (not to your previous responses!)\n'\
    'Please only enter single words; otherwise, you will receive an error message.\n'

# define trial instruction
trial_instruction = 'Please enter the first 10 different words that come to your mind.'

# create empty list to store all prompts
all_prompts = []

# Generate individual prompts for participants
for participant in participants_exp:
    exp_participant = exp[exp['participant_id'] == participant]
    participant = participant.item()
    age = exp_participant['age'].iloc[0].item()
    individual_prompt = instruction
    for trial in trials_exp:
        exp_trial = exp_participant.loc[exp_participant['trial_order'] == trial]
        if not exp_trial.empty:  # Only process if trial exists for this participant
            stimulus = exp_trial['stimulus'].iloc[0]
            responses = exp_trial['response'].iloc[0]
            spans = []
            for item in responses:
                safe = sanitize_bracket_response(str(item))
                spans.append(
                    f"<<{safe}>>" if safe is not None
                    else f'"{item}" (no response recorded)'
                )
            datapoint = f'{stimulus}. {trial_instruction} You enter {join_consecutive(spans)}\n'
            individual_prompt += datapoint
    all_prompts.append({'text': individual_prompt, 'experiment': 'guenther2024associations_individual', 'participant_id': participant, 'age': age})

# Save all prompts to JSONL file
with jsonlines.open(base_dir / "prompts.jsonl", "w") as writer:
    writer.write_all(all_prompts)

# Build the archive the repo tracks, so it is reproducible from this script
# rather than zipped by hand -- which is where the stray __MACOSX/ entries in
# several committed archives came from.
_jsonl_path = Path(base_dir / "prompts.jsonl")
_zip_path = _jsonl_path.with_name('prompts.jsonl.zip')
with zipfile.ZipFile(_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(_jsonl_path, 'prompts.jsonl')
_jsonl_path.unlink()
print('Wrote', _zip_path)
