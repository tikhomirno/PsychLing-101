import pandas as pd
import jsonlines
import os
import zipfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def generate_prompts(csv_path, output_path=None):
    if output_path is None:
        output_path = SCRIPT_DIR / 'prompts.jsonl'
    # Load the dataset
    df = pd.read_csv(csv_path)

    # Mapping conditions to the specific German questions provided
    question_map = {
        'valence': 'Wie angenehm finden Sie den eben gelesenen Text?',
        'arousal': 'Wie aufregend finden Sie den eben gelesenen Text?',
        'creativity': 'Wie kreativ finden Sie den eben gelesenen Text?',
        'boredom': 'Wie langweilig finden Sie den eben gelesenen Text?',
        'information': 'Bewerten Sie bitte den Informationsgehalt des eben gelesenen Texts. Wie informativ finden Sie den Text?'
    }

    instruction_header = (
        "Im letzten Versuchsschritt werden Ihnen nacheinander einige kurze Texte präsentiert, "
        "die Sie sorgfältig lesen und anschließend in einigen Punkten bewerten sollen.\n"
        "Bitte lesen Sie die Texte sorgfältig und bewerten Sie diese im Anschluss ohne zu "
        "lange über die Fragen nachzudenken.\n\n"
        "Response labels: '1) überhaupt nicht', '2)', '3)', '4) neutral', '5)', '6)', '7) voll und ganz'\n\n"
    )

    all_participant_data = []

    # Process by participant
    for p_id in df['participant_id'].unique():
        p_df = df[df['participant_id'] == p_id].copy()

        # Metadata extraction
        metadata = {
            "participant_id": str(p_id),
            "age": int(p_df['age'].iloc[0]) if 'age' in p_df.columns else None,
            "gender": str(p_df['gender'].iloc[0]) if 'gender' in p_df.columns else None,
            "clinical_diagnoses": str(p_df['clinical_diagnoses'].iloc[0]) if 'clinical_diagnoses' in p_df.columns else None,
            "country_of_residence": str(p_df['country_of_residence'].iloc[0]) if 'country_of_residence' in p_df.columns else None
        }

        prompt_text = instruction_header

        # Grouping by stimulus to represent a "Trial" (reading + multiple ratings)
        # We use sort=False to preserve the original order of the experiment
        grouped_trials = p_df.groupby('stimulus', sort=False)

        for i, (stimulus, trial_data) in enumerate(grouped_trials, 1):
            trial_prompt = f"Trial {i}:\n"
            trial_prompt += f"Text: \"{stimulus}\"\n"

            for _, row in trial_data.iterrows():
                q_text = question_map.get(row['condition'], f"Bewertung ({row['condition']}):")
                # Marking human response with << >>
                trial_prompt += f"  Question: {q_text} Response: <<{row['response']}>>\n"

            trial_prompt += "\n"

            # 32K Token Limit Check (Approximate: 1 token ~= 4 chars)
            # We check before adding to ensure we don't exceed the limit
            if len(prompt_text) + len(trial_prompt) > 120000:  # Safety buffer for 32k tokens
                break

            prompt_text += trial_prompt

        # Clean up trailing whitespace
        prompt_text = prompt_text.strip()

        # Construct final JSONL entry
        entry = {
            "text": prompt_text,
            "experiment": "seilerelpelt_etal2025_textratings",
            "participant_id": metadata["participant_id"],
            "age": metadata["age"],
            "gender": metadata["gender"],
            "clinical_diagnoses": metadata["clinical_diagnoses"],
            "country_of_residence": metadata["country_of_residence"]
        }

        # Remove None values
        entry = {k: v for k, v in entry.items() if v is not None}
        all_participant_data.append(entry)

    # Save to JSONL
    with jsonlines.open(output_path, mode='w') as writer:
        writer.write_all(all_participant_data)


    # Build the archive the repo tracks, so it is reproducible from this script
    # rather than zipped by hand -- which is where the stray __MACOSX/ entries in
    # several committed archives came from.
    _jsonl_path = Path(output_path)
    _zip_path = _jsonl_path.with_name('prompts.jsonl.zip')
    with zipfile.ZipFile(_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(_jsonl_path, 'prompts.jsonl')
    _jsonl_path.unlink()
    print('Wrote', _zip_path)
    print(f"Successfully generated {len(all_participant_data)} participant prompts in {_zip_path}")


if __name__ == "__main__":
    # Ensure your file is named 'data.csv' or change the string below
    csv_path = SCRIPT_DIR / 'processed_data' / 'exp1.csv'
    if csv_path.exists():
        generate_prompts(csv_path)
    else:
        print(f"File not found: {csv_path}")