import pandas as pd
import os

from pathlib import Path

# Resolve paths from this script's location so it runs from any working
# directory and always writes inside its own study folder.
SCRIPT_DIR = Path(__file__).resolve().parent

def preprocess():

    input_file = SCRIPT_DIR / "original_data" / "blp-trials.txt.zip"
    output_dir = SCRIPT_DIR / "processed_data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'exp1.csv')

    print("Loading raw dataset")
    df = pd.read_csv(input_file, sep='\t', compression='zip', low_memory=False)

    # print(df.columns)
    # for col in df:
    #     print(f"{col}: {df[col].unique()}")

    cols = [
        'participant', 
        'trial', 
        'order', 
        'block', 
        'lexicality', 
        'spelling', 
        'response', 
        'accuracy', 
        'rt'
    ]

    df = df[cols]

    df = df.rename(columns={
        'participant': 'participant_id',   
        'trial': 'trial_id',               
        'order': 'trial_order',            
        'block': 'phase_id',               
        'lexicality': 'condition',         
        'spelling': 'stimulus',            
        'response': 'response',            
        'accuracy': 'accuracy',            
        'rt': 'rt'                         
    })

    df['trial_order'] = df.groupby('participant_id').cumcount()

    print(f"Exporting preprocessed dataset to {output_file}")
    df["rt_measure"] = "keypress"
    df.to_csv(output_file, index=False)
    print("Preprocessing complete.")

if __name__ == "__main__":  
    preprocess()