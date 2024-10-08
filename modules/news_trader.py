# modules/news_trader.py (Test Module for Trading Bot)

import time
import logging
import random
from utils.news_fetcher import get_latest_news

# Configure logging to use bot.log
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Create a FileHandler and add it to the logger
file_handler = logging.FileHandler('logs/bot.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))

# Add the handler to the root logger
logger = logging.getLogger()
logger.addHandler(file_handler)

# Optional: Add a StreamHandler to log to console as well, which helps while debugging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:%(message)s'))
logger.addHandler(console_handler)

# Test logging


def run(mode, stop_event, params):
    module_name = params.get('module_name', 'News Trader')
    logging.info(f"{module_name} module started in {mode} mode with params: {params}")

    spending_cap = params.get('spending_cap', 1000)
    fetch_interval = params.get('fetch_interval', 60)  # Interval between each fetch in seconds

    while not stop_event.is_set():
        # Module logic here
        data = fetch_data()

        # Placeholder for trading logic
        logging.info(f"Fetched {len(data)} news articles")

        # Simulate trade execution
        if mode == 'real':
            # Execute real trades (for testing, we're simulating only)
            logging.info("[TEST MODE] Executing real trades... (simulation only)")
        else:
            # Simulate trades
            logging.info("Simulating trades...")

        # Sleep for a specified interval
        time.sleep(fetch_interval)

    logging.info(f"{module_name} module stopped")

def fetch_data():
    # Fetch data logic (replace with specific implementation for different modules)
    # For testing purposes, return a mock list of news articles
    return [f"News article {i}" for i in range(random.randint(5, 10))]