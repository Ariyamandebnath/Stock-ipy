import os
import sys
import csv
import time
import requests
import random
from bs4 import BeautifulSoup

csv.register_dialect(
    'mydialect',
    delimiter=',',
    quotechar='"',
    doublequote=True,
    skipinitialspace=True,
    lineterminator='\r\n',
    quoting=csv.QUOTE_MINIMAL)

class Stock:
    def __init__(self, symbol, company):
        self.symbol = symbol
        self.company = company
        self.data = []
        self.stock_price = None
        self.market_cap = None
        self.ytd_net_change = None
        self.div_amount = None
        self.div_yield = None

    def query_stock_symbol(self):
        wait_time = round(max(5, 10 + random.gauss(0, 3)), 2)
        time.sleep(wait_time)

        url = f'http://www.barrons.com/quote/stock/us/xnas/{self.symbol}'
        page = requests.get(url)
        if page.status_code == 404:
            url = f'http://www.barrons.com/quote/stock/us/xnys/{self.symbol}?mod=DNH_S'

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(e)
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        price_tag = soup.find('span', {'class': 'market__price'})
        if price_tag:
            stock_price_str = price_tag.text.replace(',', '')
            self.stock_price = float(stock_price_str) if stock_price_str != 'N/A' else None

        nutrition_tag = soup.find('div', {'class': 'nutrition'})
        if nutrition_tag:
            for b in nutrition_tag.find_all('td'):
                self.data.append(b.text)

        for i in range(len(self.data)):
            if self.data[i] == 'Market Value':
                self.market_cap = self.data[i+1]
            elif self.data[i] == 'Ytd net Change':
                self.ytd_net_change_str = self.data[i+1].strip('%')
                self.ytd_net_change = float(self.ytd_net_change_str) if self.ytd_net_change_str != 'N/A' else None
            elif self.data[i] == 'Div & Yield':
                div_amount_str, div_yield_str = self.data[i+1].split(' (')
                self.div_amount = float(div_amount_str.strip('$')) if div_amount_str != 'N/A' else None
                self.div_yield = float(div_yield_str.strip('%)')) if div_yield_str != 'N/A' else None

class Index:
    index_count = 0

    def __init__(self, name, index_link):
        self.name = name
        self.index_link = index_link
        self.index_dict = {}
        self.stock_list = []
        self.stock_data = []
        self.out_file = f'docs/{name.lower()}-dividend-stocks-sorted.csv'
        Index.index_count += 1

    def create_dict(self):
        if self.name == 'Nasdaq':
            self.create_dict_from_csv()
        elif self.name in ['S&P 500', 'Dow 30']:
            self.create_dict_from_web()

    def create_dict_from_csv(self):
        if not os.path.isfile(self.index_link):
            print(f"File not found: {self.index_link}")
            return
        with open(self.index_link) as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')
            for row in read_csv:
                if 'iShares' not in row[1] and 'iPath' not in row[1]:
                    self.index_dict[row[0]] = row[1]

    def create_dict_from_web(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        try:
            response = requests.get(self.index_link, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(e)
            return

        soup = BeautifulSoup(response.content, 'html.parser')

        if self.name == 'S&P 500':
            table = soup.find('table', {'class': 'wikitable sortable'})
            if table:
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        stock_symbol = cols[0].text.strip()
                        company_name = cols[1].text.strip()
                        self.index_dict[stock_symbol] = company_name
        elif self.name == 'Dow 30':
            table = soup.find('table', {'class': 'wikitable sortable'})
            if table:
                for row in table.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        company_name = cols[0].text.strip()
                        stock_symbol = cols[2].text.strip()
                        self.index_dict[stock_symbol] = company_name

    def add_stocks(self):
        for key, value in self.index_dict.items():
            new_stock = Stock(key, value)
            new_stock.query_stock_symbol()
            if new_stock.div_yield is not None:
                self.stock_list.append(new_stock)

        self.stock_list.sort(key=lambda stock: stock.div_yield, reverse=True)

    def from_dict_to_csv(self):
        self.add_stocks()
        self.headings = ['Company', 'Symbol', 'Current Price', 'Market Cap', 'Dividend', 'Yield', '52-Week Return']
        for stock in self.stock_list:
            new_dict = {
                'Company': stock.company,
                'Symbol': stock.symbol,
                'Current Price': stock.stock_price,
                'Market Cap': stock.market_cap,
                'Dividend': stock.div_amount,
                'Yield': f"{stock.div_yield}%" if stock.div_yield is not None else 'N/A',
                '52-Week Return': f"{stock.ytd_net_change}%" if stock.ytd_net_change is not None else 'None'
            }
            self.stock_data.append(new_dict)

        try:
            with open(self.out_file, "w", newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.headings, dialect='excel', delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for data in self.stock_data:
                    writer.writerow(data)
        except IOError as e:
            print(f"I/O error({e.errno}): {e.strerror}")

def generate_dividend_stocks():
    nasdaq_file = 'docs/dividend-stocks-nasdaq.csv'
    nasdaq_index = Index('Nasdaq', nasdaq_file)
    nasdaq_index.create_dict()
    nasdaq_index.from_dict_to_csv()

    sp_link = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    sp_index = Index('S&P 500', sp_link)
    sp_index.create_dict()
    sp_index.from_dict_to_csv()

    dow_link = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average#Components'
    dow_index = Index('Dow 30', dow_link)
    dow_index.create_dict()
    dow_index.from_dict_to_csv()

def main():
    generate_dividend_stocks()

if __name__ == '__main__':
    main()
