import os
import streamlit as st
import pandas as pd
from opto.optimizer import optimize_lineups

# Include COLUMN_CONFIG and get_logger function
import logging

# Define COLUMN_CONFIG
COLUMN_CONFIG = {
    'name': 'name',
    'position': 'pos',
    'team': 'team',
    'opponent': 'opp',
    'salary': 'dk_usd',
    'projection': 'adj_proj',  # Adjusted projection (median)
    'adjusted_projection': 'adj_proj',
    'roster_pct': 'roster_pct',
    '25th_pct': '25th_pct',
    '75th_pct': '75th_pct',
    '85th_pct': '85th_pct',
    '95th_pct': '95th_pct',
    '99th_pct': '99th_pct',
    'std_dev': 'dk_std',
    'role': 'role',  # Ensure 'role' is included
}

DEBUG = True

LOG_FILE = "nfl_app.log"
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Avoid adding multiple handlers if the logger already has them
    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(LOG_LEVEL)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = get_logger(__name__)
st.set_page_config(layout="wide")

def main():
    if 'adjusted_projections' not in st.session_state:
        st.session_state['adjusted_projections'] = {}
    df_showdown = load_and_prepare_data()
    df_showdown_combined = prepare_flex_and_captain_data(df_showdown)
    handle_user_inputs(df_showdown_combined)
    if st.session_state['adjusted_projections']:
        for player, proj in st.session_state['adjusted_projections'].items():
            df_showdown.loc[
                df_showdown[COLUMN_CONFIG['name']] == player,
                COLUMN_CONFIG['adjusted_projection']
            ] = proj
    df_showdown_combined = prepare_flex_and_captain_data(df_showdown)
    display_data_tabs(df_showdown_combined)
    optimizer_config = get_optimizer_settings(df_showdown_combined)
    if st.sidebar.button("Generate Lineups"):
        run_optimizer(optimizer_config)

def load_and_prepare_data():
    csv_dir = os.path.join(os.getcwd(), 'projections', 'out')
    if not os.path.exists(csv_dir):
        st.error(f"CSV directory not found: {csv_dir}")
        st.stop()
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    if not csv_files:
        st.error(f"No CSV files found in directory: {csv_dir}")
        st.stop()
    selected_file = st.sidebar.selectbox("Select a game to view", csv_files)
    selected_file_path = os.path.join(csv_dir, selected_file)
    df_showdown = pd.read_csv(selected_file_path)

    # Process column names to standardize
    df_showdown.columns = (
        df_showdown.columns
        .str.lower()
        .str.replace('$', '_usd')
        .str.replace('%', 'pct')
        .str.replace(r'(\d+|[a-zA-Z]+)pct$', r'\1_pct', regex=True)
        .str.replace(' ', '_')
    )

    # Verify that 'dk_usd' is in the columns
    if COLUMN_CONFIG['salary'] not in df_showdown.columns:
        st.error(f"Salary column '{COLUMN_CONFIG['salary']}' not found in data.")
        st.stop()

    df_showdown[COLUMN_CONFIG['adjusted_projection']] = df_showdown[COLUMN_CONFIG['projection']]

    return df_showdown

def handle_user_inputs(df_showdown_combined):
    st.sidebar.header("Player Settings")
    players = df_showdown_combined[COLUMN_CONFIG['name']].unique()
    flex_players = [f"{player} (Flex)" for player in players]
    captain_players = [f"{player} (Captain)" for player in players]
    player_roles = flex_players + captain_players
    selected_player_role = st.sidebar.selectbox("Select Player (Flex or Captain)", player_roles)
    if "(Flex)" in selected_player_role:
        selected_player = selected_player_role.replace(" (Flex)", "")
        selected_role = "Flex"
    elif "(Captain)" in selected_player_role:
        selected_player = selected_player_role.replace(" (Captain)", "")
        selected_role = "Captain"
    else:
        st.error("Invalid player selection.")
        st.stop()
    player_mask = (
        (df_showdown_combined[COLUMN_CONFIG['name']] == selected_player) &
        (df_showdown_combined[COLUMN_CONFIG['role']] == selected_role)
    )
    if selected_role == "Flex":
        current_proj = df_showdown_combined.loc[player_mask, COLUMN_CONFIG['adjusted_projection']].values[0]
        new_proj = st.sidebar.number_input(
            f"Adjust projection for {selected_player} ({selected_role})",
            value=float(current_proj),
            min_value=0.0,
            step=0.1
        )
        if st.sidebar.button("Update Projection"):
            st.session_state['adjusted_projections'][selected_player] = new_proj
            st.success(f"Projection for {selected_player} ({selected_role}) updated to {new_proj}")

def prepare_flex_and_captain_data(df_showdown):
    df_flex = df_showdown.copy()
    df_flex[COLUMN_CONFIG['role']] = 'Flex'

    df_captain = df_showdown.copy()
    df_captain[COLUMN_CONFIG['salary']] = df_captain[COLUMN_CONFIG['salary']] * 1.5
    df_captain[COLUMN_CONFIG['adjusted_projection']] = df_captain[COLUMN_CONFIG['adjusted_projection']] * 1.5
    df_captain[COLUMN_CONFIG['role']] = 'Captain'

    # Ensure both Flex and Captain have consistent player IDs
    df_flex['player_id'] = df_flex[COLUMN_CONFIG["name"]] + "|Flex"
    df_captain['player_id'] = df_captain[COLUMN_CONFIG["name"]] + "|Captain"

    df_showdown_combined = pd.concat([df_flex, df_captain], ignore_index=True)

    return df_showdown_combined

def display_data_tabs(df_showdown_combined):
    df_captain = df_showdown_combined[df_showdown_combined[COLUMN_CONFIG['role']] == 'Captain']
    df_flex = df_showdown_combined[df_showdown_combined[COLUMN_CONFIG['role']] == 'Flex']
    tab1, tab2 = st.tabs(["Captain Data", "Flex Data"])
    with tab1:
        st.subheader("Captain Data")
        st.dataframe(df_captain)
    with tab2:
        st.subheader("Flex Data")
        st.dataframe(df_flex)

def get_optimizer_settings(df_showdown_combined):
    st.sidebar.header("Optimizer Settings")
    num_lineups = st.sidebar.number_input("Number of Lineups to Generate", min_value=1, max_value=500, value=20)
    salary_cap = st.sidebar.slider("Salary Cap", 45000, 50000, 50000)
    apply_variance = st.sidebar.checkbox("Apply Variance for Diversity", value=True)
    min_unique_players = st.sidebar.number_input(
        "Minimum Unique Players Between Lineups",
        min_value=1, max_value=5, value=1, step=1
    )
    optimization_modes = {
        'Adjusted Projection (Median)': COLUMN_CONFIG['adjusted_projection'],
        '75th Percentile': COLUMN_CONFIG['75th_pct'],
        '85th Percentile': COLUMN_CONFIG['85th_pct'],
        '95th Percentile': COLUMN_CONFIG['95th_pct'],
        '99th Percentile': COLUMN_CONFIG['99th_pct'],
    }
    selected_mode = st.sidebar.selectbox("Optimization Mode", list(optimization_modes.keys()))
    selected_projection_column = optimization_modes[selected_mode]
    player_correlations = {}
    optimizer_config = {
        "df": df_showdown_combined,
        "num_lineups": num_lineups,
        "salary_cap": salary_cap,
        "projection_column": selected_projection_column,
        "player_correlations": player_correlations,
        "apply_variance": apply_variance,
        "mode": "optimal",
        "COLUMN_CONFIG": COLUMN_CONFIG,
        "min_unique_players": min_unique_players,
    }
    return optimizer_config

def run_optimizer(optimizer_config):
    with st.spinner('Generating lineups...'):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            lineups = optimize_lineups(
                optimizer_config,
                progress_bar=progress_bar,
                status_text=status_text
            )
            st.success("Lineup generation complete!")
            if not lineups:
                st.error("No lineups were generated. Please check your data and optimizer settings.")
                return

            # Display the generated lineups
            display_lineups(lineups, optimizer_config['df'], optimizer_config)

            # Display the exposure table
            display_exposure_table(lineups, optimizer_config['df'], optimizer_config)

        except Exception as e:
            logger.error(f"Error during optimization: {e}")
            st.error("An error occurred during optimization.")

def display_lineups(lineups, df_showdown_combined, optimizer_config):
    st.header("Generated Lineups")
    for idx, lineup in enumerate(lineups, 1):
        st.subheader(f"Lineup {idx}")
        lineup_data = []
        total_salary = 0
        total_projection = 0
        for player_id in lineup:
            name, role = player_id.split('|')
            player_info = df_showdown_combined[
                (df_showdown_combined[COLUMN_CONFIG['name']] == name) &
                (df_showdown_combined[COLUMN_CONFIG['role']] == role)
            ]
            if not player_info.empty:
                player_info = player_info.iloc[0]
                salary = player_info[COLUMN_CONFIG['salary']]
                projection = player_info[optimizer_config['projection_column']]
                total_salary += salary
                total_projection += projection
                lineup_data.append({
                    'Player': name,
                    'Role': role,
                    'Salary': salary,
                    'Projection': projection
                })
        # Sort lineup_data to place Captain at the top
        lineup_data.sort(key=lambda x: 0 if x['Role'] == 'Captain' else 1)
        lineup_df = pd.DataFrame(lineup_data)
        st.table(lineup_df)
        st.write(f"**Total Salary:** {total_salary}")
        st.write(f"**Total Projection:** {total_projection}")

def display_exposure_table(lineups, df_showdown_combined, optimizer_config):
    st.header("Player Exposure")
    player_exposure = {}
    total_lineups = len(lineups)

    for lineup in lineups:
        for player_id in lineup:
            name, role = player_id.split('|')
            key = (name, role)
            if key not in player_exposure:
                player_exposure[key] = 0
            player_exposure[key] += 1

    exposure_data = []
    for (name, role), count in player_exposure.items():
        exposure_percentage = (count / total_lineups) * 100
        exposure_data.append({
            'Player': name,
            'Role': role,
            'Lineup Count': count,
            'Exposure (%)': exposure_percentage
        })

    exposure_df = pd.DataFrame(exposure_data)
    # Sort by highest exposure
    exposure_df.sort_values(by='Exposure (%)', ascending=False, inplace=True)
    st.dataframe(exposure_df)

if __name__ == "__main__":
    main()

