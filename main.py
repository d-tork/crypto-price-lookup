#!/Users/dtork/Documents/Python/coinbase-api/venv/bin/python

import yaml 
import argparse
from coinbase.wallet.client import Client

CURRENCY_CODE = 'USD'


def main():
    args = parse_args()
    currency = args.currency

    secrets_file = 'secrets.yaml'
    secrets = read_secrets(secrets_file)

    quote = get_quote(currency=currency, secrets=secrets)
    print_answer(quote)


def parse_args():
    parser = argparse.ArgumentParser(description='Get quotes for cryptocurrencies (in USD).')
    parser.add_argument('currency', help='cryptocurrency symbol')
    return parser.parse_args()


def read_secrets(filename: str) -> dict:
    with open(filename, 'r') as f:
        secrets = yaml.safe_load(f)
    return secrets

def get_quote(currency: str, secrets: dict) -> dict:
    """Get the quote of a currency.

    If historic spot price needed, add `date` parameter to `get_spot_price` as YYYY-MM-DD

    Returns:
        API response dict, with the fields
        - amount
        - base
        - currency
    """
    coinbase_API_key = secrets['api_key']
    coinbase_API_secret = secrets['api_secret']
    client = Client(coinbase_API_key, coinbase_API_secret)

    currency = currency.upper()
    currency_pair = f"{currency}-{CURRENCY_CODE}"
    quote = client.get_spot_price(currency_pair=currency_pair)
    return quote


def print_answer(response: dict):
    """Pretty-print the quote."""
    amount = response['amount']
    base = response['base']
    currency = response['currency']
    print(f"Current price of {currency} is {amount} {base}")


if __name__ == '__main__':
    main()
