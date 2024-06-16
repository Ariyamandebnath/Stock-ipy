import pandas as pd
import numpy as np
import itertools
import math
import requests
from bs4 import BeautifulSoup

from datetime import datetime
from datetime import timedelta
from datetime import date
import time
import warnings

warnings.filterwarnings("ignore")

# Get today's date
today = date.today()

# Convert to epoch time
enddate = int(time.mktime(today.timetuple()))

# Get the starting day of the current year
starting_day_of_current_year = datetime.now().date().replace(month=1, day=1)
stdate = int(time.mktime(starting_day_of_current_year.timetuple()))

# Selenium setup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Specify the path to chromedriver
chromedriver_path = '/usr/lib/chromium-browser/chromedriver'  # Replace with the actual path

# Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the WebDriver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL for historical data
url = "https://in.investing.com/indices/s-p-cnx-nifty-historical-data?end_date={}&st_date={}".format(enddate, stdate)

# Open the URL
driver.get(url)

# Get the page source
content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

date=[]
for a in soup.findAll('td', attrs={'class':'col-rowDate'}):
    date_txt=a.find('span', attrs={'class':'text'})
    date.append(date_txt.text.strip())
    
close=[]
for a in soup.findAll('td', attrs={'class':'col-last_close'}):
    close_txt=a.find('span', attrs={'class':'text'})
    close.append(close_txt.text.strip().replace(',', ''))
#Loading Open Prices
open=[]
for a in soup.findAll('td', attrs={'class':'col-last_open'}):
    open_txt=a.find('span', attrs={'class':'text'})
    open.append(open_txt.text.strip().replace(',', ''))
#Loading High Prices
high=[]
for a in soup.findAll('td', attrs={'class':'col-last_max'}):
    high_txt=a.find('span', attrs={'class':'text'})
    high.append(high_txt.text.strip().replace(',', ''))
#Loading Low Prices
low=[]
for a in soup.findAll('td', attrs={'class':'col-last_min'}):
    low_txt=a.find('span', attrs={'class':'text'})
    low.append(low_txt.text.strip().replace(',', ''))
## Prepare DataFrame

df_nifty = pd.DataFrame({
    'Date':date,
    'Open':open,
    'High':high,
    'Low':low,
    'Close':close
    })

df_nifty.head()
    
    
# Log transformation
df_nifty['Date'] = df_nifty['Date'].astype(str).str.replace(r",","")

df_nifty['Date']=pd.to_datetime(df_nifty.Date , format = '%b %d %Y')

df_nifty=df_nifty.drop_duplicates(subset="Date")

#data = df_nifty.drop(['Date'], axis=1)
data = df_nifty

data['Close']=data['Close'].astype('float')
data['Open']=data['Open'].astype('float')
data['High']=data['High'].astype('float')
data['Low']=data['Low'].astype('float')


#data['Price']=data['Price'].astype('float')
data=data.fillna(method="ffill")
data.head()


data=data.sort_values(['Date'], ascending=[True])
data_log =    data[['Open', 'High', 'Low' , 'Close']].apply(np.log)
#data_log =    data[['Open', 'High', 'Low' , 'Price']].apply(np.log)
print(data_log)

driver.quit()
