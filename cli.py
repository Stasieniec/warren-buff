#!/usr/bin/env python3

# cli.py

import argparse
import requests
import json
import sys
import os
import time

API_URL = 'http://localhost:5000'  # Base URL for the bot's API
LOG_FILE = 'logs/bot.log'  # Log file location

# Helper function to list available modules
def list_modules(args):
    modules_dir = 'modules/'
    try:
        available_modules = [f.split('.')[0] for f in os.listdir(modules_dir) if f.endswith('.py') and f != '__init__.py']
        if available_modules:
            print("Available modules:")
            for module in available_modules:
                print(f"- {module}")
        else:
            print("No modules available.")
    except FileNotFoundError:
        print(f"Error: The modules directory '{modules_dir}' was not found.")
        sys.exit(1)

def start_module(args):
    endpoint = f'{API_URL}/start_module'
    payload = {
        'module_name': args.module_name,
        'mode': args.mode,
        'params': {}
    }

    # Add optional parameters if provided
    if args.spending_cap:
        payload['params']['spending_cap'] = args.spending_cap

    try:
        response = requests.post(endpoint, json=payload)
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the bot: {e}")
        sys.exit(1)

def stop_module(args):
    endpoint = f'{API_URL}/stop_module'
    payload = {
        'module_name': args.module_name
    }

    try:
        response = requests.post(endpoint, json=payload)
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the bot: {e}")
        sys.exit(1)

def bot_status(args):
    endpoint = f'{API_URL}/status'

    try:
        response = requests.get(endpoint)
        print_response(response)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the bot: {e}")
        sys.exit(1)

def stop_bot(args):
    print("Stopping the bot...")
    try:
        # Stop all running modules
        for module_name in get_running_modules():
            stop_module(SimpleNamespace(module_name=module_name))
        print("All modules stopped. Bot is shutting down.")
    except KeyboardInterrupt:
        print("Bot stop interrupted.")

def get_running_modules():
    endpoint = f'{API_URL}/status'
    try:
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            return data.get('running_modules', [])
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the bot: {e}")
    return []

def stream_logs(args):
    try:
        with open(LOG_FILE, 'r') as log_file:
            # Seek to the end of the file
            log_file.seek(0, os.SEEK_END)
            print("Streaming live logs. Press Ctrl+C to stop.")
            while True:
                line = log_file.readline()
                if line:
                    print(line, end='')
                else:
                    time.sleep(0.5)
    except FileNotFoundError:
        print(f"Error: The log file '{LOG_FILE}' was not found.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped streaming logs.")

def print_response(response):
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=4))
    else:
        print(f"Error: {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, indent=4))
        except json.JSONDecodeError:
            print(response.text)

from types import SimpleNamespace

def main():
    parser = argparse.ArgumentParser(description='CLI to control the trading bot.')

    subparsers = parser.add_subparsers(title='Commands', dest='command')
    subparsers.required = True

    # Start Module Command
    parser_start = subparsers.add_parser('start', help='Start a module')
    parser_start.add_argument('module_name', help='Name of the module to start')
    parser_start.add_argument('--mode', choices=['test', 'real'], default='test', help='Mode to run the module in')
    parser_start.add_argument('--spending_cap', type=float, help='Spending cap for the module')
    parser_start.set_defaults(func=start_module)

    # Stop Module Command
    parser_stop = subparsers.add_parser('stop', help='Stop a module')
    parser_stop.add_argument('module_name', help='Name of the module to stop')
    parser_stop.set_defaults(func=stop_module)

    # Stop Bot Command
    parser_stop_bot = subparsers.add_parser('stop_bot', help='Stop the entire bot')
    parser_stop_bot.set_defaults(func=stop_bot)

    # Status Command
    parser_status = subparsers.add_parser('status', help='Get the status of the bot')
    parser_status.set_defaults(func=bot_status)

    # List Modules Command
    parser_list = subparsers.add_parser('list_modules', help='List available modules')
    parser_list.set_defaults(func=list_modules)

    # Stream Logs Command
    parser_logs = subparsers.add_parser('stream_logs', help='Stream live logs of the bot')
    parser_logs.set_defaults(func=stream_logs)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()