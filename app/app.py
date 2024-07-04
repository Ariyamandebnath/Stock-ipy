import numpy as np
import pandas as pd
import streamlit as st 
import sys 
import os
from datetime import datetime, date
from keras.models import load_model
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import seaborn as sns 
from colorama import Fore

# Add the directory containing niftyScrape.py to the Python path
sys.path.append(os.path.abspath("/home/ariyaman/learntocode/Stockipy/scraper"))
import niftyScrape


st.set_page_config(page_title="StockiPy", page_icon="🐍")

# Define the scraping function
def scrapeData(starting_date, ending_date, stock):
    symbol = stock 
    fromDate = datetime.combine(starting_date, datetime.min.time())
    tillDate = datetime.combine(ending_date, datetime.min.time())
    outputPath = f"/home/ariyaman/learntocode/Stockipy/data/historical_stock_data_{symbol}.csv"
    
    def progressCallback(progress):
        progress_bar.progress(progress)

    with st.spinner("Scraping data..."):
        niftyScrape.stock_csv(symbol, fromDate, tillDate, series="EQ", output=outputPath, show_progress=True, progress_callback=progressCallback)
    
    return outputPath

# Page title and description
st.markdown('<h1 style="text-align: center;">StockiPy</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center;">Stock Price Predictor</h3>', unsafe_allow_html=True)


nifty_50_stocks = {
    "ADANIPORTS": "Adani Ports and Special Economic Zone Ltd",
    "ASIANPAINT": "Asian Paints Ltd",
    "AXISBANK": "Axis Bank Ltd",
    "BAJAJ-AUTO": "Bajaj Auto Ltd",
    "BAJFINANCE": "Bajaj Finance Ltd",
    "BAJAJFINSV": "Bajaj Finserv Ltd",
    "BPCL": "Bharat Petroleum Corporation Ltd",
    "BHARTIARTL": "Bharti Airtel Ltd",
    "BRITANNIA": "Britannia Industries Ltd",
    "CIPLA": "Cipla Ltd",
    "COALINDIA": "Coal India Ltd",
    "DIVISLAB": "Divi's Laboratories Ltd",
    "DRREDDY": "Dr. Reddy's Laboratories Ltd",
    "EICHERMOT": "Eicher Motors Ltd",
    "GRASIM": "Grasim Industries Ltd",
    "HCLTECH": "HCL Technologies Ltd",
    "HDFCBANK": "HDFC Bank Ltd",
    "HDFC": "Housing Development Finance Corporation Ltd",
    "HEROMOTOCO": "Hero MotoCorp Ltd",
    "HINDALCO": "Hindalco Industries Ltd",
    "HINDUNILVR": "Hindustan Unilever Ltd",
    "ICICIBANK": "ICICI Bank Ltd",
    "ITC": "ITC Ltd",
    "INDUSINDBK": "IndusInd Bank Ltd",
    "INFY": "Infosys Ltd",
    "JSWSTEEL": "JSW Steel Ltd",
    "KOTAKBANK": "Kotak Mahindra Bank Ltd",
    "LT": "Larsen & Toubro Ltd",
    "M&M": "Mahindra & Mahindra Ltd",
    "MARUTI": "Maruti Suzuki India Ltd",
    "NTPC": "NTPC Ltd",
    "NESTLEIND": "Nestle India Ltd",
    "ONGC": "Oil and Natural Gas Corporation Ltd",
    "POWERGRID": "Power Grid Corporation of India Ltd",
    "RELIANCE": "Reliance Industries Ltd",
    "SBIN": "State Bank of India",
    "SUNPHARMA": "Sun Pharmaceutical Industries Ltd",
    "TCS": "Tata Consultancy Services Ltd",
    "TATAMOTORS": "Tata Motors Ltd",
    "TATASTEEL": "Tata Steel Ltd",
    "TECHM": "Tech Mahindra Ltd",
    "TITAN": "Titan Company Ltd",
    "ULTRACEMCO": "UltraTech Cement Ltd",
    "UPL": "UPL Ltd",
    "WIPRO": "Wipro Ltd"
}

left, right = st.columns(2)

with left:
    stockSymbol = st.selectbox("Select the Stock you'd like to predict", list(nifty_50_stocks.keys()))
    
    companyName = nifty_50_stocks[stockSymbol]
    st.write(f"You selected: {stockSymbol} - {companyName}")

with right:
    SelectedModel = st.selectbox("Select the Machine Learning model to implement", ("LSTM (Long short-term memory)", "GRU (Gated Recurrent Unit)", "ARIMA (Autoregressive integrated moving average)"))

# Date input widgets for starting and ending dates
starting_date = st.date_input("Starting Date", date(2013, 1, 1))
ending_date = st.date_input("Ending Date", date(2024, 6, 27))

scrape = st.button("Scrape Data")

if scrape:
    path = scrapeData(starting_date, ending_date, stockSymbol)
    data = pd.read_csv(path)
    st.write(data)

    # Data styling
    st.dataframe(data.style.highlight_max(axis=0, color='lightblue'))

    # Plot the data
    fig = px.line(data, x='Date', y='Close', title=f'{stock} Closing Prices')
    st.plotly_chart(fig)
    