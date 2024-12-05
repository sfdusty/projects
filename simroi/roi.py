import pandas as pd
from itertools import combinations  # Import combinations

# Load data from CSV
data = pd.read_csv("lineup_data.csv")

# List of positional columns
position_columns = ['PG', 'SG', 'SF', 'PF', 'C', 'G', 'F', 'UTIL']

# Generate three-player combination features
trio_combinations = []
for col1, col2, col3 in combinations(position_columns, 3):
    trio_name = f"{col1}_{col2}_{col3}_comb"
    data[trio_name] = data[col1].astype(str) + "_" + data[col2].astype(str) + "_" + data[col3].astype(str)
    trio_combinations.append(trio_name)

# Analyze profitability of each three-player combination
results = []

for trio in trio_combinations:
    # Group by the trio combination
    grouped = data.groupby(trio).agg(
        avg_roi=('Simulated ROI', 'mean'),
        count=('Simulated ROI', 'count'),
        avg_proj_score=('Proj Score', 'mean'),
        player_ids=(trio, 'unique')  # Include unique player combinations
    ).reset_index()

    # Add trio name for context
    grouped['combination'] = trio
    results.append(grouped)

# Combine all results into a single DataFrame
results_df = pd.concat(results, ignore_index=True)

# Filter for combinations that appear frequently enough (e.g., count > 3)
filtered_combinations = results_df[results_df['count'] > 3]

# Sort by avg_roi to find most and least profitable combinations
most_profitable_trios = filtered_combinations.sort_values(by='avg_roi', ascending=False).head(20)
least_profitable_trios = filtered_combinations.sort_values(by='avg_roi', ascending=True).head(20)

# Analyze single players in specific roster spots
single_player_results = []

for position in position_columns:
    grouped = data.groupby(position).agg(
        avg_roi=('Simulated ROI', 'mean'),
        count=('Simulated ROI', 'count'),
        avg_proj_score=('Proj Score', 'mean')
    ).reset_index()

    grouped['position'] = position
    single_player_results.append(grouped)

# Combine single-player results into a single DataFrame
single_player_df = pd.concat(single_player_results, ignore_index=True)

# Filter for players appearing frequently enough (e.g., count > 3)
filtered_single_players = single_player_df[single_player_df['count'] > 3]

# Find the single most and least profitable plays
most_profitable_single = filtered_single_players.sort_values(by='avg_roi', ascending=False).head(10)
least_profitable_single = filtered_single_players.sort_values(by='avg_roi', ascending=True).head(10)

# Save results to CSV for review
most_profitable_trios.to_csv("most_profitable_trios.csv", index=False)
least_profitable_trios.to_csv("least_profitable_trios.csv", index=False)
most_profitable_single.to_csv("most_profitable_single.csv", index=False)
least_profitable_single.to_csv("least_profitable_single.csv", index=False)

# Print the results
print("Top 10 Most Profitable Three-Player Combinations:")
print(most_profitable_trios[['combination', 'avg_roi', 'count', 'avg_proj_score', 'player_ids']])

print("\nTop 10 Least Profitable Three-Player Combinations:")
print(least_profitable_trios[['combination', 'avg_roi', 'count', 'avg_proj_score', 'player_ids']])

print("\nTop 10 Most Profitable Single Players in Roster Spots:")
print(most_profitable_single[['position', 'avg_roi', 'count', 'avg_proj_score']])

print("\nTop 10 Least Profitable Single Players in Roster Spots:")
print(least_profitable_single[['position', 'avg_roi', 'count', 'avg_proj_score']])
