# ui/lineup_display.py

import streamlit as st
import pandas as pd
from settings import COLUMN_CONFIG


def display_lineups(lineups, exposure_df, df_showdown):
    """
    Displays the selected lineups in a tiled format and shows player exposures after selection.

    Parameters:
    - lineups (list): List of selected lineups to display.
    - exposure_df (pd.DataFrame): DataFrame containing exposure data.
    - df_showdown (pd.DataFrame): Original DataFrame with player data.
    """
    st.header("Optimized Lineups")

    if not lineups:
        st.warning("No lineups to display.")
        return

    # Calculate number of rows needed
    num_lineups = len(lineups)
    lineups_per_row = 3
    num_rows = (num_lineups + lineups_per_row - 1) // lineups_per_row

    lineup_idx = 0
    for row in range(num_rows):
        cols = st.columns(lineups_per_row)
        for col_idx in range(lineups_per_row):
            if lineup_idx >= num_lineups:
                break
            lineup = lineups[lineup_idx]
            with cols[col_idx]:
                st.subheader(f"Lineup #{lineup_idx + 1}")
                lineup_details = []
                lineup_salary = 0
                lineup_projection = 0

                # Extract player details and sort captain first
                for player_id in lineup:
                    try:
                        name, role = player_id.rsplit('|', 1)
                        player_info = df_showdown[
                            (df_showdown[COLUMN_CONFIG['name']] == name) &
                            (df_showdown['role'] == role)
                        ]
                        if player_info.empty:
                            st.error(f"Player data not found for: {player_id}")
                            continue
                        player_info = player_info.iloc[0]

                        player_entry = {
                            'Player': f"{name} ({role})",
                            'Salary': player_info[COLUMN_CONFIG['salary']],
                            'Projection': player_info[COLUMN_CONFIG['adjusted_projection']]
                        }
                        lineup_details.append(player_entry)

                        lineup_salary += player_info[COLUMN_CONFIG['salary']]
                        lineup_projection += player_info[COLUMN_CONFIG['adjusted_projection']]
                    except Exception as e:
                        st.error(f"Error retrieving data for player {player_id}: {e}")
                        continue

                # Sort lineup details to have captain first
                lineup_details.sort(key=lambda x: 0 if '(Captain)' in x['Player'] else 1)

                # Convert to DataFrame for display
                lineup_df = pd.DataFrame(lineup_details)

                # Format salary and projection for better readability
                lineup_df['Salary'] = lineup_df['Salary'].apply(lambda x: f"${x:,.0f}")
                lineup_df['Projection'] = lineup_df['Projection'].apply(lambda x: f"{x:.2f}")

                # Display lineup table
                st.table(lineup_df[['Player', 'Salary', 'Projection']])

                # Display lineup summary
                st.write(f"**Total Salary:** ${lineup_salary:,.0f}")
                st.write(f"**Total Projection:** {lineup_projection:.2f}")
            lineup_idx += 1

    # Display Player Exposure After Selection
    st.header("Player Exposure After Selection")
    # Format exposure_df for better readability
    exposure_df_display = exposure_df[['Player', 'Role', 'Salary', 'Projection', 'Current Exposure (%)']]
    exposure_df_display['Salary'] = exposure_df_display['Salary'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
    exposure_df_display['Projection'] = exposure_df_display['Projection'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
    st.dataframe(exposure_df_display)


def display_exposure(exposure_df):
    """
    Displays the player exposure table and allows users to set target exposures.

    Parameters:
    - exposure_df (pd.DataFrame): DataFrame containing current exposure data.

    Returns:
    - pd.DataFrame: DataFrame updated with user-defined target exposures.
    """
    st.header("Player Exposure in Pool")

    # Create a table-like layout with multiple columns
    # Define the number of columns per row
    cols_per_row = 3
    total_players = len(exposure_df)
    num_rows = (total_players + cols_per_row - 1) // cols_per_row

    # Initialize a list to store target exposures
    target_exposures = []

    for row in range(num_rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            idx = row * cols_per_row + col_idx
            if idx >= total_players:
                break
            row_data = exposure_df.iloc[idx]
            with cols[col_idx]:
                st.subheader(f"{row_data['Player']} ({row_data['Role']})")
                st.write(f"**Current Exposure:** {row_data['Current Exposure (%)']}%")
                target_exposure = st.number_input(
                    f"Target Exposure (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=row_data['Current Exposure (%)'],
                    step=1.0,
                    key=f"{row_data['Player']}_{row_data['Role']}_exposure"
                )
                target_exposures.append(target_exposure)

    # Assign target exposures back to the DataFrame
    exposure_df['Target Exposure (%)'] = target_exposures

    # Display the exposure DataFrame
    exposure_df_display = exposure_df[['Player', 'Role', 'Salary', 'Projection', 'Current Exposure (%)', 'Target Exposure (%)']]
    exposure_df_display['Salary'] = exposure_df_display['Salary'].apply(lambda x: f"${x:,.0f}" if pd.notnull(x) else "N/A")
    exposure_df_display['Projection'] = exposure_df_display['Projection'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A")
    st.dataframe(exposure_df_display)

    return exposure_df

