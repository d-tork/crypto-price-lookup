import yaml 
import argparse
from datetime import datetime
from coinbase.wallet.client import Client

CURRENCY_CODE = 'USD'


def main():
    args = parse_args()
    currency = args.currency
    try:
        quote_date = validate_passed_date(passed_date=args.date)
    except TypeError:
        quote_date = None

    secrets_file = 'secrets.yaml'
    secrets = read_secrets(secrets_file)

    quote = get_quote(currency=currency, secrets=secrets, date=quote_date)
    print_answer(quote)


def parse_args():
    parser = argparse.ArgumentParser(description='Get quotes for cryptocurrencies (in USD).')
    parser.add_argument('currency', help='cryptocurrency symbol')
    parser.add_argument('-d', '--date', help='as-of date for quote')
    return parser.parse_args()


def validate_passed_date(passed_date: str) -> str:
    """Ensure the date passed as an arg conforms to the expected format.

    If it does not, fill in with today's date. 

    Raises:
        TypeError: If no date is passed via command line, and a current quote is desired.

    """
    if not passed_date:
        raise TypeError
    expected_format = '%Y-%m-%d'
    try:
        datetime.strptime(passed_date, expected_format)
    except ValueError:
        return datetime.today().strftime(expected_format)
    else:
        return passed_date


def read_secrets(filename: str) -> dict:
    with open(filename, 'r') as f:
        secrets = yaml.safe_load(f)
    return secrets


def get_quote(currency: str, secrets: dict, date: str=None) -> dict:
    """Get the quote of a currency.

    Args:
        currency: Three-letter currency symbol/ticker to query.
        secrets: Key and password for Coinbase API.
        date: Date for which to fetch historic quote, as YYYY-MM-DD. Optional.
            If no date is passed, the current quote is fetched.

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
    quote = client.get_spot_price(currency_pair=currency_pair, date=date)
    quote['date'] = datetime.today().strftime('%Y-%m-%d')
    return quote


def print_answer(response: dict):
    """Pretty-print the quote."""
    print("{date} price of {currency}: {amount} {base}".format(**response))


if __name__ == '__main__':
    main()
