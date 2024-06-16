import os
import json
import itertools
import csv
from pprint import pprint
from urllib.parse import urljoin
from requests import Session
import click
from datetime import datetime, timedelta

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None

APP_NAME = "nsehistory"

def break_dates(from_date, to_date, delta=timedelta(days=30)):
    """
    Breaks date range into chunks of given delta (30 days by default)
    """
    current_date = from_date
    while current_date <= to_date:
        end_date = min(current_date + delta, to_date)
        yield (current_date, end_date)
        current_date = end_date + timedelta(days=1)

def np_date(x):
    return pd.to_datetime(x, format="%d-%b-%Y")

def np_float(x):
    try:
        return float(x.replace(",", ""))
    except:
        return float("nan")

def np_int(x):
    try:
        return int(x.replace(",", ""))
    except:
        return 0

def pool(func, params, max_workers=2):
    """
    A simple thread pool implementation to parallelize API calls
    """
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(lambda p: func(*p), params)
    return list(results)

class NSEHistory:
    def __init__(self):
        self.headers = {
            "Host": "www.nseindia.com",
            "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=SBIN",
            "X-Requested-With": "XMLHttpRequest",
            "pragma": "no-cache",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
        self.path_map = {
            "stock_history": "/api/historical/cm/equity",
            "derivatives": "/api/historical/fo/derivatives",
            "equity_quote_page": "/get-quotes/equity",
        }
        self.base_url = "https://www.nseindia.com"
        self.cache_dir = ".cache"
        self.workers = 2
        self.use_threads = True
        self.show_progress = False

        self.s = Session()
        self.s.headers.update(self.headers)
        self.ssl_verify = True

    def _get(self, path_name, params):
        if "nseappid" not in self.s.cookies:
            path = self.path_map["equity_quote_page"]
            url = urljoin(self.base_url, path)
            self.s.get(url, verify=self.ssl_verify)
        path = self.path_map[path_name]
        url = urljoin(self.base_url, path)
        self.r = self.s.get(url, params=params, verify=self.ssl_verify)
        return self.r

    def _stock(self, symbol, from_date, to_date, series="EQ"):
        params = {
            'symbol': symbol,
            'from': from_date.strftime('%d-%m-%Y'),
            'to': to_date.strftime('%d-%m-%Y'),
            'series': '["{}"]'.format(series),
        }
        self.r = self._get("stock_history", params)
        j = self.r.json()
        return j['data']

    def stock_raw(self, symbol, from_date, to_date, series="EQ"):
        date_ranges = break_dates(from_date, to_date)
        params = [(symbol, x[0], x[1], series) for x in reversed(list(date_ranges))]
        chunks = pool(self._stock, params, max_workers=self.workers)
        return list(itertools.chain.from_iterable(chunks))

stock_select_headers = [
    "CH_TIMESTAMP", "CH_SERIES",
    "CH_OPENING_PRICE", "CH_TRADE_HIGH_PRICE",
    "CH_TRADE_LOW_PRICE", "CH_PREVIOUS_CLS_PRICE",
    "CH_LAST_TRADED_PRICE", "CH_CLOSING_PRICE",
    "VWAP", "CH_52WEEK_HIGH_PRICE", "CH_52WEEK_LOW_PRICE",
    "CH_TOT_TRADED_QTY", "CH_TOT_TRADED_VAL", "CH_TOTAL_TRADES",
    "CH_SYMBOL"
]
stock_final_headers = [
    "DATE", "SERIES",
    "OPEN", "HIGH",
    "LOW", "PREV. CLOSE",
    "LTP", "CLOSE",
    "VWAP", "52W H", "52W L",
    "VOLUME", "VALUE", "NO OF TRADES", "SYMBOL"
]
stock_dtypes = [
    np_date, str,
    np_float, np_float,
    np_float, np_float,
    np_float, np_float,
    np_float, np_float, np_float,
    np_int, np_float, np_int, str
]

def stock_csv(symbol, from_date, to_date, series="EQ", output="", show_progress=True):
    h = NSEHistory()
    h.show_progress = show_progress

    date_ranges = break_dates(from_date, to_date)
    params = [(symbol, x[0], x[1], series) for x in reversed(list(date_ranges))]
    
    if show_progress:
        with click.progressbar(params, label=symbol) as ps:
            chunks = []
            for p in ps:
                r = h.stock_raw(*p)
                chunks.append(r)
            raw = list(itertools.chain.from_iterable(chunks))
    else:
        raw = h.stock_raw(symbol, from_date, to_date, series)

    if not output:
        output = "{}-{}-{}-{}.csv".format(symbol, from_date, to_date, series)
    if raw:
        with open(output, 'w') as fp:
            fp.write(",".join(stock_final_headers) + '\n')
            for row in raw:
                row_select = [str(row[x]) for x in stock_select_headers]
                line = ",".join(row_select) + '\n'
                fp.write(line) 
    return output

def stock_df(symbol, from_date, to_date, series="EQ"):
    if not pd:
        raise ModuleNotFoundError("Please install pandas using \n pip install pandas")
    h = NSEHistory()
    raw = h.stock_raw(symbol, from_date, to_date, series)
    df = pd.DataFrame(raw)[stock_select_headers]
    df.columns = stock_final_headers
    for i, h in enumerate(stock_final_headers):
        df[h] = df[h].apply(stock_dtypes[i])
    return df

if __name__ == "__main__":
    symbol = 'SBIN'
    from_date = datetime.strptime('01-01-2023', '%d-%m-%Y')
    to_date = datetime.strptime('31-05-2023', '%d-%m-%Y')
    stock_csv(symbol, from_date, to_date, series="EQ", output="historical_stock_data.csv", show_progress=True)
