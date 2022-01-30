# Coinbase API Connector

Fetch quotes for cryptocurrencies. 

There's no reason to use the different APIs for single vs. multiple; I'm simply playing with both.

It seems as though I am required to authenticate myself to the regular Coinbase API, but not to
the Pro version. However, neither has bulk endpoints so you have to loop through coin names one
at a time anyway. The script `pro.py` does this in chunks of 10 followed by a short sleep to 
abide by the rate limits.

# Single token - Coinbase API
using [`coinbase`](https://github.com/coinbase/coinbase-python/) which, although officially from
Coinbase, is deprecated & archived.

```bash
./main.py BTC
```

# Multiple tokens - Coinbase Pro API
using [`cbpro`](https://github.com/danpaquin/coinbasepro-python)

```
# currency_list.txt
BTC
ETH
YFI
AMP
```
```bash
./pro.py currency_list.txt
```

Alternatively, could try [`coinbasepro`](https://github.com/acontry/coinbasepro)

## References
* [Coinbase API - get spot prices](https://developers.coinbase.com/api/v2#get-spot-price)
* [Coinbase Pro API (which sucks)](https://docs.cloud.coinbase.com/exchange/docs)
* 
