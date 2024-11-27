import pandas as pd

columns = ['freq', 'task', 'sub', 'block', 'Fp1', 'Fz', 'F3', 'F7', 'FT9', 'FC5', 'FC1', 'C3', 'T7', 'TP9', 'CP5', 'CP1', 'Pz', 'P3', 'P7', 'O1', 'Oz', 'O2', 'P4', 'P8', 'TP10', 'CP6', 'CP2', 'Cz', 'C4', 'T8', 'FT10', 'FC6', 'FC2', 'F4', 'F8', 'Fp2', 'AF7', 'AF3', 'AFz', 'F1', 'F5', 'FT7', 'FC3', 'C1', 'C5', 'TP7', 'CP3', 'P1', 'P5', 'PO7', 'PO3', 'POz', 'PO4', 'PO8', 'P6', 'P2', 'CPz', 'CP4', 'TP8', 'C6', 'C2', 'FC4', 'FT8', 'F6', 'AF8', 'AF4', 'F2', 'Iz']

freq_unique = ['Alpha', 'Beta', 'Delta', 'Theta']
task_unique = ['В', 'К', 'М', 'Р']
block_unique = [1, 2, 3]
df_path = 'data/norm_var_7class.csv'

exhaust_df_path = 'data/Class7Fatigue.csv'

# Add file paths for all tables
input_files = {
    'К': 'data/CombFunction7.csv',
    'В': 'data/VisualSearch7.csv',
    'Р': 'data/WorkingMemory7.csv',
    'М': 'data/MentalArithmetic7.csv'
}

def get_attention_value(norm_df, subject, task):
    """Get attention value for specific subject and task"""
    try:
        # Convert subject from 7XX to XX format
        orig_subject = int(str(subject)[1:])
        
        # Filter base conditions (Alpha band, block 1, current task)
        base_conditions = (
            (norm_df['freq'] == 'Alpha') & 
            (norm_df['block'] == 1) & 
            (norm_df['task'] == task)
        )
        
        # Get all values for these conditions to calculate percentiles
        base_filtered = norm_df.loc[base_conditions]
        
        # Calculate 90th percentile for each channel we might need
        channels = ['F6', 'F4', 'F8', 'FC6']
        percentiles = {
            channel: base_filtered[channel].quantile(0.9)
            for channel in channels
        }
        
        # Get subject's specific row
        subject_conditions = base_conditions & (norm_df['sub'] == orig_subject)
        subject_row = norm_df.loc[subject_conditions]
        
        if subject_row.empty:
            return None
            
        # Check F6 first
        if subject_row['F6'].iloc[0] <= percentiles['F6']:
            return subject_row['F6'].iloc[0]
            
        # If F6 exceeds 90th percentile, try alternative channels
        for alt_channel in ['F4', 'F8', 'FC6']:
            if subject_row[alt_channel].iloc[0] <= percentiles[alt_channel]:
                return subject_row[alt_channel].iloc[0]
        
        # If all channels exceed their 90th percentiles, return None
        return None
        
    except Exception as e:
        print(f"Error processing subject {subject} for task {task}: {str(e)}")
        return None

def process_tables():
    # Read source dataframes
    exhaust_df = pd.read_csv(exhaust_df_path)
    norm_df = pd.read_csv(df_path)
    
    # Convert sub column in norm_df to 7XX format and create subject_id column
    norm_df['subject_id'] = norm_df['sub'].apply(lambda x: int(f"7{x:02d}"))
    
    # Set indexes for easier lookup
    exhaust_df.set_index('subject', inplace=True)
    
    # Process each input file
    for task_letter, file_path in input_files.items():
        # Read input table
        df = pd.read_csv(file_path)
        
        # Add diff column from exhaust_df using index
        df['diff'] = df['subject'].apply(
            lambda x: exhaust_df.loc[x, 'diff'] if x in exhaust_df.index else None
        )
        
        df['error_percentage'] = (1 - df['answer']) * 100
        
        # Add attention column
        df['attention'] = df['subject'].apply(
            lambda x: get_attention_value(norm_df, x, task_letter)
        )
        
        # Save modified table
        output_path = file_path.replace('.csv', '_modified.csv')
        df.to_csv(output_path, index=False)

if __name__ == "__main__":
    process_tables()