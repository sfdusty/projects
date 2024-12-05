def adjust_percentiles(input_file, output_file):
    # Load the processed CSV file
    data = pd.read_csv(input_file)

    # Ensure no division by zero by replacing zero Base Proj with NaN
    data['Base Proj'] = data['Base Proj'].replace(0, pd.NA)
    
    # Calculate the adjustment ratio
    data['Adjustment Ratio'] = data['Adj Proj'] / data['Base Proj']

    # Adjust the percentile columns
    for percentile in ["50th%", "75th%", "85th%", "95th%"]:
        data[percentile] = data[percentile] * data['Adjustment Ratio']

    # Drop the temporary Adjustment Ratio column
    data = data.drop(columns=['Adjustment Ratio'])

    # Standardize numerical formatting to 2 decimal places for the updated columns
    numerical_columns = ["50th%", "75th%", "85th%", "95th%"]
    data[numerical_columns] = data[numerical_columns].applymap(lambda x: round(x, 2))

    # Save the adjusted data to a new CSV file
    data.to_csv(output_file, index=False)

    return output_file


