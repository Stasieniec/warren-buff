# utils/alpaca_utils.py
import os
import logging
import alpaca_trade_api as tradeapi
import json

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


# Alpaca API credentials from environment variables
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = "https://paper-api.alpaca.markets/v2"

# Connect to Alpaca API
# Alpaca API credentials from environment variables
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = "https://paper-api.alpaca.markets/v2"

# Path to store module-related data
data_directory = 'data/'
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# Function to load module state
def load_module_state(module_name):
    filepath = f'{data_directory}{module_name}_state.json'
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    else:
        return {
            "max_money_per_day": 0,
            "max_money_per_transaction": 0,
            "history": []
        }

# Function to save module state
def save_module_state(module_name, state):
    filepath = f'{data_directory}{module_name}_state.json'
    with open(filepath, 'w') as file:
        json.dump(state, file, indent=4)

# Connect to Alpaca API
def connect_to_alpaca():
    try:
        api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')
        logging.info("Connected to Alpaca API.")
        return api
    except Exception as e:
        logging.error(f"Failed to connect to Alpaca API: {str(e)}")
        raise

# Buy stock
def buy_stock(symbol, quantity, module_name):
    api = connect_to_alpaca()
    state = load_module_state(module_name)
    max_per_transaction = state.get("max_money_per_transaction", 0)
    market_price = get_market_price(symbol) * quantity
    
    if market_price > max_per_transaction:
        logging.warning(f"Buy order for {symbol} exceeds max money per transaction limit.")
        return None
    
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        logging.info(f"Buy order placed for {quantity} shares of {symbol}.")
        state["history"].append({"action": "buy", "symbol": symbol, "quantity": quantity, "price": market_price, "timestamp": time.time()})
        save_module_state(module_name, state)
        return order
    except Exception as e:
        logging.error(f"Failed to place buy order for {symbol}: {str(e)}")
        raise

# Sell stock
def sell_stock(symbol, quantity, module_name):
    api = connect_to_alpaca()
    state = load_module_state(module_name)
    
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='sell',
            type='market',
            time_in_force='gtc'
        )
        logging.info(f"Sell order placed for {quantity} shares of {symbol}.")
        market_price = get_market_price(symbol) * quantity
        state["history"].append({"action": "sell", "symbol": symbol, "quantity": quantity, "price": market_price, "timestamp": time.time()})
        save_module_state(module_name, state)
        return order
    except Exception as e:
        logging.error(f"Failed to place sell order for {symbol}: {str(e)}")
        raise

# Get order status
def get_order_status(order_id):
    api = connect_to_alpaca()
    try:
        order = api.get_order(order_id)
        logging.info(f"Order status for {order_id}: {order.status}")
        return order.status
    except Exception as e:
        logging.error(f"Failed to get order status for {order_id}: {str(e)}")
        raise

# Cancel order
def cancel_order(order_id):
    api = connect_to_alpaca()
    try:
        api.cancel_order(order_id)
        logging.info(f"Order {order_id} canceled.")
    except Exception as e:
        logging.error(f"Failed to cancel order {order_id}: {str(e)}")
        raise

# Get account information
def get_account_info():
    api = connect_to_alpaca()
    try:
        account = api.get_account()
        logging.info("Retrieved account information.")
        return account
    except Exception as e:
        logging.error(f"Failed to retrieve account information: {str(e)}")
        raise

# Get position information
def get_position(symbol):
    api = connect_to_alpaca()
    try:
        position = api.get_position(symbol)
        logging.info(f"Retrieved position for {symbol}.")
        return position
    except Exception as e:
        logging.error(f"Failed to retrieve position for {symbol}: {str(e)}")
        raise

# Close position
def close_position(symbol):
    api = connect_to_alpaca()
    try:
        api.close_position(symbol)
        logging.info(f"Closed position for {symbol}.")
    except Exception as e:
        logging.error(f"Failed to close position for {symbol}: {str(e)}")
        raise

# Get market price
def get_market_price(symbol):
    api = connect_to_alpaca()
    try:
        barset = api.get_barset(symbol, 'minute', limit=1)
        bar = barset[symbol][0]
        logging.info(f"Retrieved market price for {symbol}: {bar.c}")
        return bar.c
    except Exception as e:
        logging.error(f"Failed to get market price for {symbol}: {str(e)}")
        raise