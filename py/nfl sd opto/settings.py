import logging

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
}


DEBUG = True

LOG_FILE = "nfl_app.log"
LOG_LEVEL = logging.DEBUG if DEBUG else logging.INFO

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(LOG_LEVEL)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

