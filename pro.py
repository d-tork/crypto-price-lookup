#!/Users/dtork/Documents/Python/coinbase-api/venv/bin/python
"""
Use the Coinbase Pro API to bulk get prices.

"""

import argparse
import cbpro
import pandas as pd
from time import sleep
from datetime import datetime


class CoinbaseProClient(cbpro.PublicClient):
    def __init__(self):
        super().__init__()

    def get_quotes(self, currencies: list) -> dict:
        """Fetch quotes for all currencies, manually throttling."""
        quote_mappings = {}
        num_requests = len(currencies)
        num_chunks = (num_requests // 10) + 1 

        for i in range(num_chunks):
            chunk_start = i*10
            chunk_end = chunk_start+10
            chunk = currencies[chunk_start:chunk_end]
            print(chunk)

            fetched_quotes = [self._get_quote(coin) for coin in chunk]
            quote_update = {coin: quote for coin, quote in zip(chunk, fetched_quotes)}
            quote_mappings.update(quote_update)
            sleep(2)
        return quote_mappings

    def _get_quote(self, currency):
        for base_currency in ['USD', 'USDC', 'USDT']:
            currency_pair = f'{currency}-{base_currency}'
            quote_data =  self.get_product_ticker(product_id=currency_pair)
            try:
                return quote_data['price']
            except KeyError:
                continue
        return None



def main():
    args = parse_args()

    input_currencies = get_input_currency_list(filepath=args.infile)

    cb_client = CoinbaseProClient()
    mapped_quotes = cb_client.get_quotes(currencies=input_currencies)
    df_quotes = convert_quotes_to_df(quotes=mapped_quotes)
    write_df_to_file(df_quotes)


def parse_args():
    parser = argparse.ArgumentParser(description='Get quotes for cryptocurrencies (in USD).')
    parser.add_argument('infile', help='Plain text list of cryptocurrencies')
    return parser.parse_args()


def get_input_currency_list(filepath: str) -> list:
    with open(filepath, 'r') as f:
        lines = f.readlines()
        clean_lines = [x.strip() for x in lines]
        return clean_lines


def convert_quotes_to_df(quotes: dict) -> pd.DataFrame:
    df = pd.DataFrame.from_dict(quotes, orient='index').reset_index()
    df.columns = ['currency', 'price_usd']
    return df


def write_df_to_file(df: pd.DataFrame):
    timestamp = datetime.now()
    ts_format = '%Y-%m-%d_%H%M_%S'
    ts_formatted = timestamp.strftime(ts_format)
    outname = f'crypto_prices_as_of_{ts_formatted}.csv'
    df.to_csv(outname, index=False)
    return


if __name__ == '__main__':
    main()

