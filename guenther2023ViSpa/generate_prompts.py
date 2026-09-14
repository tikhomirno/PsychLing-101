import pandas as pd
import jsonlines
from pathlib import Path

# load data‚
base_dir = Path(__file__).parent.resolve()
df = pd.read_csv(base_dir / "processed_data" / "exp1.csv")

# Sort dataframe by participant ID and trial order
df = df.sort_values(by=['participant_id', 'trial_id'])

# Remap participant IDs to sequential integers starting from 1
df['participant_id'] = df['participant_id'].map({p: i+1 for i, p in enumerate(df.participant_id.unique())})

# Get unique participants and trial indices
participants = df['participant_id'].unique()
trials = range(df['trial_id'].max() + 1)

# Define experiment instructions shown to participants
instruction = """Instructions\n
In the following study, you will be presented with sets of four word pairs.\n
Your task is to judge which of the objects described by these four pairs look the most similar and which the least similar. Of course, you will have to pick two different pairs for these two questions.\n
As an example, consider the four following pairs:\n
bottle - pyramid\ndog - wolf\nlamp - soldier\ncar - street\n
A reasonable answer in this case could be that dog - wolf look the most similar, while car - street look the least similar.\n
Note that you should only consider visual similarity for this task, and ignore other types of similarity (for example, even though cars and roads often occur together, they do not look similar).\n
The study will not continue unless you give a response. Thus, if you want to pause the study, you can delay your response until you want to continue.\n
By pressing the ESC key, you will end the fullscreen mode. This does not hinder you from continuing the experiment, but you cannot switch back to fullscreen mode. If possible, we want to ask you to stay in fullscreen mode for the whole duration of the experiment.\n
The study will start with two practice trials in which you receive feedback.\n"""

# Generate individual prompts for each participant
all_prompts = []
for participant in participants:
    # Get data for current participant
    df_participant = df[df['participant_id'] == participant]
    participant = participant.item()
    
    # Start with instruction text
    prompt = instruction
    
    # Add each trial's word and response
    for trial in trials:
        df_trial = df_participant.loc[df_participant['trial_id'] == trial]
        if not df_trial.empty:
            # Extract word and participant's response
            stimulus = df_trial['stimulus'].iloc[0]
            best = df_trial['best'].iloc[0]
            worst = df_trial['worst'].iloc[0]
            datapoint = f'Which look the most similar? {stimulus}. You choose <<{best}>> as most similar. Which look the least similar? {stimulus}. You choose <<{worst}>> as least similar \n '
            prompt += datapoint
            
    prompt += '\n'
    
    # Store complete prompt with metadata
    all_prompts.append({
        'text': prompt,
        'experiment': 'guenther2023ViSpa',
        'participant_id': participant,
        # Per-trial reaction times in ms, in the same order as the trials above.
        'rt': df_participant['rt'].tolist(),
    })

# Save all prompts to JSONL file
with jsonlines.open(base_dir / 'prompts.jsonl', 'w') as writer:
    writer.write_all(all_prompts)

# Package the deliverable. The repository layout requires
# <study>/prompts.jsonl.zip containing a single entry named prompts.jsonl;
# this script previously wrote only the loose .jsonl, so the committed archive
# had to be produced by hand.
import zipfile

jsonl_path = base_dir / 'prompts.jsonl'
with zipfile.ZipFile(base_dir / 'prompts.jsonl.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(jsonl_path, 'prompts.jsonl')
jsonl_path.unlink()
print(f"Wrote {base_dir / 'prompts.jsonl.zip'}")
