# data_manager.py
import pandas as pd
import os

def load_data(boats_file):
    """Load boat data from CSV."""
    return pd.read_csv(boats_file)

def load_history(history_file):
    """Load history data from CSV if it exists, return empty DataFrame otherwise."""
    if os.path.exists(history_file):
        loaded_data = pd.read_csv(history_file)
        if not loaded_data.empty and 'status' in loaded_data.columns:
            completed = loaded_data[loaded_data['status'] == 'completed'].drop(columns=['status'])
            missed = loaded_data[loaded_data['status'] == 'missed'].drop(columns=['status'])
            return completed, missed
    return pd.DataFrame(), pd.DataFrame()

def save_history(completed_boats, missed_boats, history_file):
    """Save completed and missed boats to history file."""
    completed = completed_boats.copy()
    completed['status'] = 'completed'
    missed = missed_boats.copy()
    missed['status'] = 'missed'
    combined_df = pd.concat([completed, missed], ignore_index=True)
    combined_df.to_csv(history_file, index=False)