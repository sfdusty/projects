import pandas as pd
import logging
import os
from outcome_adj import adjust_percentiles

# Determine the base directory (nfl/data/code/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the base directory
LOG_FILE_PATH = os.path.join(BASE_DIR, '../out/function.log')
INPUT_DIR = os.path.join(BASE_DIR, '../csvs/input/')
OUTPUT_DIR = os.path.join(BASE_DIR, '../out/')

# Ensure the output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

def combined_clean_ppd(df):
    logging.info("function call: combined_clean_ppd started")
    try:
        required_columns = [
            'Name', 'Pos', 'Team', 'Opp', 'Salary', 'SS Proj', 'Live Proj', 'My Own', 
            'dk_25_percentile', 'dk_50_percentile', 'dk_75_percentile', 'dk_85_percentile', 
            'dk_95_percentile', 'dk_99_percentile', 'dk_std'
        ]
        df_filtered = df[required_columns]
        df_filtered = df_filtered[df_filtered['dk_75_percentile'].notna()]
        df_filtered['Salary'] = pd.to_numeric(df_filtered['Salary'], errors='coerce')
        df_filtered = df_filtered.sort_values(by=['Name', 'Salary'])
        
        if df_filtered['Name'].duplicated().any():
            duplicated_names = df_filtered[df_filtered['Name'].duplicated(keep=False)]
            for name in duplicated_names['Name'].unique():
                name_rows = df_filtered[df_filtered['Name'] == name]
                captain_row = name_rows[name_rows['Salary'] == name_rows['Salary'].max()]
                df_filtered = df_filtered.drop(captain_row.index)
        
        df_deduped = df_filtered.drop_duplicates(subset='Name', keep='first')
        df_deduped['Live Proj'] = df_deduped['Live Proj'].fillna(df_deduped['SS Proj'])
        df_deduped = df_deduped.rename(columns={
            'Salary': 'DK$', 'My Own': 'Roster%', 'dk_25_percentile': '25th%', 
            'dk_50_percentile': '50th%', 'dk_75_percentile': '75th%', 
            'dk_85_percentile': '85th%', 'dk_95_percentile': '95th%', 
            'dk_99_percentile': '99th%'
        })
        df_deduped.columns = df_deduped.columns.str.lower()
        df_deduped['adj_proj_ppd'] = df_deduped['adj_proj'] / df_deduped['dk$'] * 1000
        df_deduped['25th_ppd'] = df_deduped['25th%'] / df_deduped['dk$'] * 1000
        df_deduped['50th_ppd'] = df_deduped['50th%'] / df_deduped['dk$'] * 1000
        df_deduped['75th_ppd'] = df_deduped['75th%'] / df_deduped['dk$'] * 1000
        df_deduped['85th_ppd'] = df_deduped['85th%'] / df_deduped['dk$'] * 1000
        df_deduped['95th_ppd'] = df_deduped['95th%'] / df_deduped['dk$'] * 1000
        df_deduped['99th_ppd'] = df_deduped['99th%'] / df_deduped['dk$'] * 1000
        logging.info("function call: combined_clean_ppd ran successfully")
        return df_deduped
    except Exception as e:
        logging.error(f"function call: combined_clean_ppd failed due to error - {str(e)}")
        raise

def sort_by_salary_descending(df):
    logging.info("function call: sort_by_salary_descending started")
    try:
        df_sorted = df.sort_values(by='dk$', ascending=False)
        logging.info("Data successfully sorted by dk$ in descending order")
        return df_sorted
    except Exception as e:
        logging.error(f"function call: sort_by_salary_descending failed due to error - {str(e)}")
        raise

def adjust_roster_percentage(df):
    logging.info("function call: adjust_roster_percentage started")
    try:
        df['roster%'] = df['roster%'] / 100
        logging.info("Roster% successfully adjusted to be between 0 and 1")
        return df
    except Exception as e:
        logging.error(f"function call: adjust_roster_percentage failed due to error - {str(e)}")
        raise

def round_columns(df):
    logging.info("function call: round_columns started")
    try:
        df['roster%'] = df['roster%'].round(3)
        ppd_columns = ['adj_proj_ppd', '25th_ppd', '50th_ppd', '75th_ppd', '85th_ppd', '95th_ppd', '99th_ppd']
        df[ppd_columns] = df[ppd_columns].round(3)
        percentile_columns = ['25th%', '50th%', '75th%', '85th%', '95th%', '99th%']
        df[percentile_columns] = df[percentile_columns].round(2)
        logging.info("Columns successfully rounded")
        return df
    except Exception as e:
        logging.error(f"function call: round_columns failed due to error - {str(e)}")
        raise

def process_file(df, adjustment_factor=1.0):
    cleaned_df = combined_clean_ppd(df)
    adjusted_df = adjust_percentiles(cleaned_df, adjustment_factor)
    sorted_df = sort_by_salary_descending(adjusted_df)
    adjusted_roster_df = adjust_roster_percentage(sorted_df)
    final_df = round_columns(adjusted_roster_df)
    return final_df

def extract_team_abbreviations(filename):
    try:
        teams_part = filename.split('-@-')
        if len(teams_part) == 2:
            # Extract last 3 characters of the first team and first 3 of the second
            team1 = ''.join(filter(str.isalpha, teams_part[0][-3:]))
            team2 = ''.join(filter(str.isalpha, teams_part[1][:3]))
            teams = f"{team1}_{team2}"
            return teams
        return "Unknown_Teams"
    except Exception as e:
        logging.error(f"Error extracting team abbreviations from {filename}: {str(e)}")
        return "Unknown_Teams"

def delete_existing_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"Deleted existing file: {filepath}")
    except Exception as e:
        logging.error(f"Error deleting file: {filepath}. Error: {str(e)}")

def main():
    # Ensure input directory exists
    if not os.path.isdir(INPUT_DIR):
        logging.error(f"Input directory does not exist: {INPUT_DIR}")
        return

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.csv'):
            input_filepath = os.path.join(INPUT_DIR, filename)
            try:
                df = pd.read_csv(input_filepath)
                logging.info(f"Processing file: {input_filepath}")
                processed_df = process_file(df)
                teams_abbreviation = extract_team_abbreviations(filename)
                output_file = os.path.join(OUTPUT_DIR, f'{teams_abbreviation}.csv')
                
                # Delete the existing file if it exists
                delete_existing_file(output_file)
                
                # Save the processed DataFrame to the output directory
                processed_df.to_csv(output_file, index=False)
                logging.info(f"Processed file saved to {output_file}")
            except Exception as e:
                logging.error(f"Failed to process file {filename}: {str(e)}")

if __name__ == "__main__":
    main()

