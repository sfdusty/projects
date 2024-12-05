import pandas as pd

def process_draftkings_csv(input_file, output_file):
    # Load the raw CSV file
    dk_data = pd.read_csv(input_file)

    # Step 1: Remove captain rows
    flex_data = dk_data[~dk_data['Salary'].isin(dk_data['Salary'] * 1.5)]

    # Step 2: Filter to keep only the necessary columns
    columns_to_keep = [
        "Name", "Pos", "Team", "Opp", "Salary", "SS Proj", 
        "My Proj", "My Own", "Saber Team", 
        "dk_50_percentile", "dk_75_percentile", 
        "dk_85_percentile", "dk_95_percentile"
    ]
    filtered_data = flex_data[columns_to_keep]

    # Step 3: Rename columns
    renamed_data = filtered_data.rename(columns={
        "SS Proj": "Base Proj",
        "My Proj": "Adj Proj",
        "My Own": "Roster%",
        "Saber Team": "Team Total",
        "dk_50_percentile": "50th%",
        "dk_75_percentile": "75th%",
        "dk_85_percentile": "85th%",
        "dk_95_percentile": "95th%"
    })

    # Step 4: Add value columns for percentile outcomes
    for percentile in ["50th%", "75th%", "85th%", "95th%"]:
        value_column = f"{percentile} Value"
        renamed_data[value_column] = (renamed_data[percentile] / renamed_data["Salary"]) * 1000

    # Step 5: Standardize numerical formatting to 2 decimal places
    numerical_columns = renamed_data.select_dtypes(include=['float64', 'int64']).columns
    renamed_data[numerical_columns] = renamed_data[numerical_columns].applymap(lambda x: round(x, 2))

    # Save the processed data to a new CSV file
    renamed_data.to_csv(output_file, index=False)
    
    


