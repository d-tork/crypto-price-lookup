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

    def get_quotes(self, currencies: list, date: str) -> dict:
        """Fetch quotes for all currencies, manually throttling.

        Args:
            currencies: List of 3-letter ticker symbols.
            date: Date for which to fetch historic quote, as YYYY-MM-DD. 
                Can be None, in which case the current quote is fetched.
        """
        quote_mappings = {}
        num_requests = len(currencies)
        num_chunks = (num_requests // 10) + 1 

        for i in range(num_chunks):
            chunk_start = i*10
            chunk_end = chunk_start+10
            chunk = currencies[chunk_start:chunk_end]
            print(chunk)

            fetched_quotes = [self._get_quote(coin, date) for coin in chunk]
            quote_update = {coin: quote for coin, quote in zip(chunk, fetched_quotes)}
            quote_mappings.update(quote_update)
            sleep(2)
        return quote_mappings

    def _get_quote(self, currency: str, date: str):
        for base_currency in ['USD', 'USDC', 'USDT']:
            currency_pair = f'{currency}-{base_currency}'
            if date:
                candle_resp = self.get_product_historic_rates(product_id=currency_pair, 
                                                              start=date, 
                                                              end=date,
                                                              granularity=86400)
                quote_data = self._parse_historic_candle_data(response=candle_resp)
            else:
                quote_data =  self.get_product_ticker(product_id=currency_pair)

            try:
                return quote_data['price']
            except KeyError:
                continue
        return None

    @staticmethod
    def _parse_historic_candle_data(response: list) -> dict:
        """Adds field names to raw candle response.

        Uses the first record regardless of how many candles are returned, assuming
        that granularity was set to 86400 (one per day) and the date range was a
        single date.
        """
        response_fields = 'time low high open close volume'.split()
        candle_data = {k: v for k, v in zip(response_fields, response[0])}
        candle_data['price'] = candle_data['close']
        return candle_data


def main():
    args = parse_args()
    try:
        quote_date = validate_passed_date(passed_date=args.date)
    except TypeError:
        quote_date = None

    input_currencies = get_input_currency_list(filepath=args.infile)

    cb_client = CoinbaseProClient()
    mapped_quotes = cb_client.get_quotes(currencies=input_currencies, date=quote_date)

    label_date = quote_date if quote_date else datetime.now().strftime('%Y-%m-%d')
    df_quotes = convert_quotes_to_df(quotes=mapped_quotes, date=label_date)
    write_df_to_file(df_quotes, date=label_date)


def parse_args():
    parser = argparse.ArgumentParser(description='Get quotes for cryptocurrencies (in USD).')
    parser.add_argument('infile', help='Plain text list of cryptocurrencies')
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


def get_input_currency_list(filepath: str) -> list:
    with open(filepath, 'r') as f:
        lines = f.readlines()
        clean_lines = [x.strip() for x in lines]
        return clean_lines


def convert_quotes_to_df(quotes: dict, date: str) -> pd.DataFrame:
    df = pd.DataFrame.from_dict(quotes, orient='index').reset_index()
    df.columns = ['currency', 'price_usd']
    df['date'] = date
    return df


def write_df_to_file(df: pd.DataFrame, date: str):
    date_format = '%Y-%m-%d'
    ts_format = '%Y-%m-%d_%H%M_%S'
    timestamp = datetime.strptime(date, date_format)
    ts_formatted = timestamp.strftime(ts_format)

    outname = f'crypto_prices_as_of_{ts_formatted}.csv'
    df.to_csv(outname, index=False)
    return


if __name__ == '__main__':
    main()

