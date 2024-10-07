# Trading Bot

This is a modular trading bot built in Python that allows users to create, start, stop, and monitor various trading strategies through a REST API and command-line interface (CLI). The bot integrates with the Alpaca trading API for trading U.S. stocks and supports both paper trading and live trading modes. Each trading strategy is implemented as a separate module, making the system easy to extend and customize.

## Features
- **Modular Trading Strategies**: Add and manage trading strategies as independent modules.
- **REST API with Flask**: Start, stop, and monitor trading modules through a REST API.
- **Command-Line Interface**: Simple CLI to interact with the bot.
- **Alpaca API Integration**: Trade stocks using Alpaca's API for both paper and live trading.
- **State Management**: Save module state and parameters to JSON files for easy persistence.
- **Logging**: All events and errors are logged to `bot.log`.
- **Error Recovery**: Automatically restart modules if they stop unexpectedly.

## Requirements
- Python 3.8+
- Alpaca API Account (for trading)
- Dependencies listed in `requirements.txt`:
  - Flask
  - requests
  - termcolor
  - alpaca-trade-api

## Installation
1. **Clone the Repository**
   ```sh
   git clone https://github.com/your-username/trading-bot.git
   cd trading-bot

2. Install Dependencies     
    ```
    pip install -r requirements.txt    
    ```


3. Set Up Environment Variables Set your Alpaca API credentials as environment variables:
    ```
    export ALPACA_API_KEY='your_alpaca_api_key'
    export ALPACA_SECRET_KEY='your_alpaca_secret_key'
    ```


## Usage    
### Starting the Bot    
Run the main bot script
```
python bot.py
```
This will start the Flask server and the main loop for monitoring modules     

### REST API Endpoints
- Start a Module: Start a trading module by sending a POST request to `/start_module`.
    ```
    POST /start_module
    {
    "module_name": "news_trader",
    "mode": "test",
    "params": {
        "max_money_per_day": 1000,
        "max_money_per_transaction": 500
    }
    }
```
- Stop a Module: Stop a running module by sending a POST request to `/stop_module`.
    ```
    POST /stop_module
    {
    "module_name": "news_trader"
    }
    ```

- Check Status: Get the status of the bot and running modules by sending a GET request to `/status`.
    ```
    GET /status
    ```


### Command-Line Interface (CLI)
The bot also has a command-line interface for easier interaction:
```sh
# Start a Module
python cli.py start <module_name> --mode test --spending_cap 1000

# Stop a Module
python cli.py stop <module_name>

# Check Status
python cli.py status

# Stream Logs
python cli.py stream_logs   


## File Structure
- bot.py: Core of the bot. Manages modules, API, and main execution loop.
- cli.py: Command-line interface for interacting with the bot.
- modules/: Directory containing trading strategy implementations.
    - news_trader.py: Example module using news data for trading decisions.
- utils/: Contains utility scripts for configuration, state management, Alpaca API interactions, etc.
    - alpaca_utils.py: Connects to Alpaca API, manages trades.
    - configuration_utils.py: Manages configuration loading.
    - state_utils.py: Manages saving and backing up bot state.
- logs/: Directory containing logs (bot.log).
- config/: Configuration files.
- params/: Stores parameters for each module.     


## Module Development
To create a new trading module, add a Python script to the `modules/` directory. Each module should define a `run(mode, stop_event, params)` function to implement the trading logic.

Example Template (`example_module.py`):
```python
import time
import logging

def run(mode, stop_event, params):
    logging.info(f"Example Module started in {mode} mode with params: {params}")
    while not stop_event.is_set():
        # Trading logic here
        time.sleep(60)  # Run every minute
    logging.info("Example Module stopped")

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.


## License
This project is licensed under the [Beerware license](https://en.wikipedia.org/wiki/Beerware)    