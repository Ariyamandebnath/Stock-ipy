"""Program to collect and present stock market data for Nasdaq, S&P 500, and Dow 30 indexes."""
import os
import sys
import math
import csv
import time
import itertools
import bisect
import urllib2
import urllib
import string
import requests
import random
import bs4
from bs4 import BeautifulSoup

csv.register_dialect(
    'mydialect',
    delimiter = ',',
    quotechar = '"',
    doublequote = True,
    skipinitialspace = True,
    lineterminator = '\r\n',
    quoting = csv.QUOTE_MINIMAL)

class Stock:
    def __init__(self, symbol, company):
        self.symbol = symbol
        self.company = company
        self.data = []

    def query_stock_symbol(self):
        # Add wait times in between getting each player's data to prevent overload
        wait_time = round(max(5, 10 + random.gauss(0,3)), 2)
        time.sleep(wait_time)

        # Check for two different Barron's URLs
        url = 'http://www.barrons.com/quote/stock/us/xnas/%s' % (self.symbol)
        page = requests.get(url)
        if page.status_code == 404:
            url = 'http://www.barrons.com/quote/stock/us/xnys/%s?mod=DNH_S' % (self.symbol)

        # Create a new URL request
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        headers = { 'User-Agent' : user_agent }
        req = urllib2.Request(url, headers=headers)

        # Catch potential URL error
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            print e.reason

        # Create BeautifulSoup object
        self.soup = BeautifulSoup(response, 'html.parser')

        # Find stock price
        for a in self.soup.findAll('span', {'class':'market__price'}):
            print a.text
            stock_price_str = a.text.replace(',', '')
            if stock_price_str != 'N/A':
                self.stock_price = float(stock_price_str)
            else:
                self.stock_price = None

        # Append remaining data
        for a in self.soup.findAll('div', {'class': 'nutrition'}):
            for b in a.findAll('td'):
                print b.text
                self.data.append(b.text)

        # Extract remaining data
        self.market_cap = None
        for i in xrange(0, len(self.data)):
            if self.data[i] == 'Market Value':
                self.market_cap = self.data[i+1]
            elif self.data[i] == 'Ytd net Change':
                self.ytd_net_change_str = self.data[i+1].strip('%')
                if self.ytd_net_change_str != 'N/A':
                    self.ytd_net_change = float(self.ytd_net_change_str)
                else:
                    self.ytd_net_change = -1
            elif self.data[i] == 'Div & Yield':
                div_amount_str = self.data[i+1].split(' (')[0].strip(' ')
                div_amount_str = div_amount_str.strip('$')
                div_yield_str = self.data[i+1].split(' (')[1].strip(')')
                div_yield_str = div_yield_str.strip('%')
                if div_amount_str != 'N/A':
                    self.div_amount = float(div_amount_str)
                    self.div_yield = float(div_yield_str)
                else:
                    self.div_amount = None
                    self.div_yield = None

class Index:
    'Common base class for all indexes'
    index_count = 0

    def __init__(self, name, index_link):
        self.name = name
        #self.index_file = index_file
        self.index_link = index_link
        self.index_dict = {}
        self.stock_list = []
        self.stock_data = []
        self.out_file = 'docs/' + name.lower() + '-dividend-stocks-sorted.csv'
        Index.index_count += 1

    def create_dict(self):
        if self.name == 'Nasdaq':
            self.create_dict_from_csv()
        elif self.name == 'S&P 500' or self.name == 'Dow 30':
            self.create_dict_from_web()

    def create_dict_from_csv(self):
        with open(self.index_link) as csv_file:
            read_csv = csv.reader(csv_file, delimiter=',')
            for row in read_csv:
                if row[1].find('iShares') == -1 and row[1].find('iPath') == -1:
                    self.index_dict[row[0]] = row[1]

    def create_dict_from_web(self):
        # Create a new URL request
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        headers = { 'User-Agent' : user_agent }
        url = self.index_link
        req = urllib2.Request(url, headers=headers)

        # Catch potential URL error
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            print e.reason

        # Create BeautifulSoup object
        self.soup = BeautifulSoup(response, 'html.parser')

        #store the list of components in a dictionary by ticker symbol
        if self.name == 'S&P 500':
            for a in self.soup.findAll('table', {'class': 'wikitable sortable'}, limit=1):
                for b in a.findAll('tr'):
                    count = 1
                    for c in b.findAll('td', limit=2):
                        if count == 1:
                            stock_symbol = c.text
                            count += 1
                        elif count == 2:
                            company_name = c.text
                            self.index_dict[stock_symbol] = company_name
                            count = 1
        elif self.name == 'Dow 30':
            for a in self.soup.findAll('table', {'class': 'wikitable sortable'}):
                for b in a.findAll('tr'):
                    count = 1
                    for c in b.findAll('td', limit=3):
                        if count == 1:
                            company_name = c.text
                            count += 1
                        elif count == 2:
                            count += 1
                        elif count == 3:
                            stock_symbol = c.text
                            self.index_dict[stock_symbol] = company_name
                            count = 1

    def add_stocks(self):
        for key, value in self.index_dict.items():
            new_stock = Stock(key, value)
            new_stock.query_stock_symbol()
            if new_stock.div_yield != None:
                self.stock_list.append(new_stock)

        #Sort the stock list by yield amount, in desecending order
        self.stock_list.sort(key=lambda stock: stock.div_yield, reverse=True)

    def from_dict_to_csv(self):
        self.add_stocks()
        self.headings = ['Company','Symbol','Current Price','Market Cap','Dividend', 'Yield', '52-Week Return']
        for i in xrange(0, len(self.stock_list)):
            new_dict = {}
            new_dict['Company'] = self.stock_list[i].company
            new_dict['Symbol'] = self.stock_list[i].symbol
            new_dict['Current Price'] = self.stock_list[i].stock_price
            new_dict['Market Cap'] = self.stock_list[i].market_cap
            new_dict['Dividend'] = self.stock_list[i].div_amount
            if self.stock_list[i].div_yield != None:
                new_dict['Yield'] = str(self.stock_list[i].div_yield) + '%'
            else:
                new_dict['Yield'] = 'N/A'
            if self.stock_list[i].ytd_net_change != None:
                new_dict['52-Week Return'] = str(self.stock_list[i].ytd_net_change) + '%'
            else:
                new_dict['52-Week Return'] = 'None'
            self.stock_data.append(new_dict)

        try:
            with open(self.out_file, "wb") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.headings, dialect='excel', delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
                writer.writeheader()
                for data in self.stock_data:
                    writer.writerow(data)

        except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)

def generate_dividend_stocks():
    nasdaq_file = '../docs/dividend-stocks-nasdaq.csv'
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
    sys.exit(main())