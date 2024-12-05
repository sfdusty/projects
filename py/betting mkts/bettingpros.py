import os
import requests
import json
from datetime import datetime

# Configuration
DEBUG_MODE = True
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "x-api-key": "CHi8Hy5CEE4khd46XNYL23dCFX96oUdw6qOt1Dnh"  # Provided API key
}
api_config = {
    "base_url": "https://api.bettingpros.com/v3",
    "location": "OH",
    "sport": "NFL",
    "limit": 16,
    "season": 2024,
    "week": 6
}
bookie_map = {
    12: "DraftKings",
    10: "FanDuel",
    19: "BetMGM",
    13: "Caesars"
}
event_statuses_to_skip = {"closed", "complete"}

# Data directory setup
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Points to assistant/
data_dir = os.path.join(root_dir, "data")
os.makedirs(data_dir, exist_ok=True)

# Data files
lines_file = os.path.join(data_dir, 'lines.json')
event_info_file = os.path.join(data_dir, 'event_info.json')

# Initialize the main data structure
events_data = {}

def load_existing_event_info():
    """Load existing event_info.json if it exists."""
    if os.path.exists(event_info_file):
        with open(event_info_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {event_info_file} is not a valid JSON. Starting fresh.")
    return {}

def fetch_events():
    """Fetch events from the API and include their status."""
    url = f"{api_config['base_url']}/events?sport={api_config['sport']}&week={api_config['week']}&season={api_config['season']}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    events = response.json().get('events', [])
    event_info = {}
    for event in events:
        event_id = str(event['id'])
        event_info[event_id] = {
            'event_id': event_id,
            'home': event['participants'][1]['name'],
            'away': event['participants'][0]['name'],
            'scheduled': event['scheduled'],
            'status': event.get('status', '').lower()
        }
    return event_info

def save_event_info(event_info):
    """Save the updated event info to a JSON file."""
    with open(event_info_file, 'w') as f:
        json.dump(event_info, f, indent=4)
    print(f"Event information saved to {event_info_file}")

def fetch_offers(market_id, event_ids):
    """Fetch offers from the API for the given market and event IDs."""
    offers = []
    base_url = api_config['base_url'].rstrip("/")
    event_id_str = ','.join(event_ids)
    url = f"{base_url}/offers?sport={api_config['sport']}&market_id={market_id}&event_id={event_id_str}&location={api_config['location']}&limit={api_config['limit']}&page=1"
    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        offers.extend(data.get("offers", []))
        next_url = data.get('_pagination', {}).get('next')
        url = f"{base_url}{next_url}" if next_url else None
    return offers

def process_market(event_info, market_name, market_id):
    """Process a specific market for all relevant events."""
    print(f"Processing {market_name.capitalize()}...\n")
    
    # Filter event IDs based on status
    active_event_ids = [
        event_id for event_id, info in event_info.items()
        if info.get('status') not in event_statuses_to_skip
    ]
    
    if not active_event_ids:
        print(f"No active events to process for {market_name}.\n")
        return
    
    offers = fetch_offers(market_id=market_id, event_ids=active_event_ids)
    for offer in offers:
        event_id = str(offer.get('event_id'))
        if event_id not in event_info:
            continue
        event = event_info[event_id]
        if event.get('status') in event_statuses_to_skip:
            continue  # Skip processing for this event
        
        if event_id not in events_data:
            # Initialize the event data
            events_data[event_id] = {
                'event_id': event_id,
                'home': event['home'],
                'away': event['away'],
                'scheduled': event['scheduled'],
                'markets': {}
            }
        markets = events_data[event_id]['markets']
        if market_name not in markets:
            markets[market_name] = {}
        for selection in offer.get('selections', []):
            label = selection.get('label')  # Team label or Over/Under
            for book in selection.get('books', []):
                bookie_id = book.get('id')
                bookie_name = bookie_map.get(bookie_id)
                if not bookie_name:
                    # Skip bookies not in the bookie_map
                    continue
                if bookie_name not in markets[market_name]:
                    markets[market_name][bookie_name] = []
                for line in book.get('lines', []):
                    timestamp = datetime.utcnow().isoformat() + 'Z'  # UTC time in ISO format
                    line_data = {
                        'timestamp': timestamp,
                        'bookie': bookie_name
                    }
                    if market_name == 'moneyline':
                        line_data.update({
                            'team': label,
                            'odds': line.get('cost')
                        })
                    elif market_name == 'spread':
                        line_data.update({
                            'team': label,
                            'spread': line.get('line'),
                            'odds': line.get('cost')
                        })
                    elif market_name == 'total':
                        line_data.update({
                            'over_under': label,
                            'total_points': line.get('line'),
                            'odds': line.get('cost')
                        })
                    markets[market_name][bookie_name].append(line_data)
                    if DEBUG_MODE:
                        print(f"Saved {market_name} for event {event_id}, {label}, bookie {bookie_name}")
    print(f"Completed processing {market_name.capitalize()}.\n")

def main():
    # Load existing event info
    existing_event_info = load_existing_event_info()
    
    # Fetch latest events from API
    fetched_event_info = fetch_events()
    
    # Update existing event info with fetched data
    updated_event_info = existing_event_info.copy()
    for event_id, info in fetched_event_info.items():
        updated_event_info[event_id] = info  # This will add new events and update existing ones
    
    # Save the updated event info
    save_event_info(updated_event_info)
    
    # Prepare list of active event IDs (status not in skip list)
    active_event_ids = [
        event_id for event_id, info in updated_event_info.items()
        if info.get('status') not in event_statuses_to_skip
    ]
    
    if not active_event_ids:
        print("No active events to process.")
        return
    
    # Process each market
    process_market(updated_event_info, 'moneyline', 1)  # Market ID 1 for Moneylines
    process_market(updated_event_info, 'spread', 3)     # Market ID 3 for Spreads
    process_market(updated_event_info, 'total', 2)      # Market ID 2 for Totals

    # Save the events_data to lines.json
    with open(lines_file, 'w') as f:
        json.dump(events_data, f, indent=4)
    print(f"All lines saved to {lines_file}")

if __name__ == "__main__":
    main()

