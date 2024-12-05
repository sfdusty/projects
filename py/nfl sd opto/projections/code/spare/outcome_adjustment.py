import pandas as pd
import logging
from datetime import datetime

# Set up logging configuration
logging.basicConfig(filename='community_function.log', 
                    level=logging.INFO, 
                    format='%(asctime)s %(message)s')

def roo_adjust(df, adjustment_factor=1.0):
    # Log the start of the function
    logging.info("function call: roo_adjust started")

    try:
        # Create a copy of the original percentiles and std for comparison later
        original_df = df.copy()

        adjustment_needed = df[df['proj'] != df['adj_proj']]
        
        if adjustment_needed.empty:
            df = df.drop(columns=['adj_proj'])
            logging.info("function call: roo_adjust ran successfully - no adjustment needed")
            return df, original_df
        
        for idx, row in adjustment_needed.iterrows():
            # Calculate a direct proportional shift based on adj_proj and the tunable adjustment factor
            shift_factor = (row['adj_proj'] / row['proj']) * adjustment_factor

            # Adjust the percentiles using the shift factor
            adjusted_25th = max(0, row['25th%'] * shift_factor)
            adjusted_50th = max(0, row['50th%'] * shift_factor)
            adjusted_75th = row['75th%'] * shift_factor
            adjusted_85th = row['85th%'] * shift_factor
            adjusted_95th = row['95th%'] * shift_factor
            adjusted_99th = row['99th%'] * shift_factor

            # Adjust the standard deviation using the same shift factor
            adjusted_dk_std = row['dk_std'] * shift_factor

            # Update the adjusted values back into the dataframe
            df.at[idx, '25th%'] = adjusted_25th
            df.at[idx, '50th%'] = adjusted_50th
            df.at[idx, '75th%'] = adjusted_75th
            df.at[idx, '85th%'] = adjusted_85th
            df.at[idx, '95th%'] = adjusted_95th
            df.at[idx, '99th%'] = adjusted_99th
            df.at[idx, 'dk_std'] = adjusted_dk_std

        # Log successful run
        logging.info("function call: roo_adjust ran successfully")
        # Keep the 'proj' column to ensure we can track differences
        return df, original_df

    except Exception as e:
        # Log any error that occurs
        logging.error(f"function call: roo_adjust failed due to error - {str(e)}")
        raise

