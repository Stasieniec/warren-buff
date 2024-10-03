# cli.py

import click
import requests
import json
import sys
from rich import print as rprint

API_URL = 'http://localhost:5000'  # Base URL for the bot's API

def print_response(response):
    if response.status_code == 200:
        data = response.json()
        rprint(f"[bold green]{json.dumps(data, indent=4)}[/bold green]")
    else:
        rprint(f"[bold red]Error: {response.status_code}[/bold red]")
        try:
            data = response.json()
            rprint(f"[red]{json.dumps(data, indent=4)}[/red]")
        except json.JSONDecodeError:
            rprint(response.text)

@click.group()
def cli():
    """CLI to control the trading bot."""
    pass

@cli.command()
@click.argument('module_name')
@click.option('--mode', default='test', type=click.Choice(['test', 'real']), help='Mode to run the module in')
@click.option('--spending_cap', type=float, help='Spending cap for the module')
def start(module_name, mode, spending_cap):
    """Start a module."""
    endpoint = f'{API_URL}/start_module'
    payload = {
        'module_name': module_name,
        'mode': mode,
        'params': {}
    }

    if spending_cap:
        payload['params']['spending_cap'] = spending_cap

    try:
        response = requests.post(endpoint, json=payload)
        print_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Error connecting to the bot: {e}", fg='red', err=True)
        sys.exit(1)

@cli.command()
@click.argument('module_name')
def stop(module_name):
    """Stop a module."""
    endpoint = f'{API_URL}/stop_module'
    payload = {'module_name': module_name}

    try:
        response = requests.post(endpoint, json=payload)
        print_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Error connecting to the bot: {e}", fg='red', err=True)
        sys.exit(1)

@cli.command()
def status():
    """Get the status of the bot."""
    endpoint = f'{API_URL}/status'

    try:
        response = requests.get(endpoint)
        print_response(response)
    except requests.exceptions.RequestException as e:
        click.secho(f"Error connecting to the bot: {e}", fg='red', err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()
