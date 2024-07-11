import pandas as pd
import streamlit as st
import sys
import os
from datetime import datetime, date
import plotly.express as px

# Add the directory containing niftyScrape.py to the Python path
sys.path.append(os.path.abspath("/home/ariyaman/learntocode/Stockipy/scraper"))

import niftyScrape
from helper import delete_files_except_one

st.set_page_config(page_title="StockiPy", page_icon="🐍")



# Custom CSS for styling and animations
st.markdown(
    """
    <style>
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    @keyframes slideIn {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(0); }
    }
    .fadeIn {
        animation: fadeIn 2s ease-in-out;
    }
    .slideIn {
        animation: slideIn 1s ease-out;
    }
    .center {
        text-align: center;
    }
    .header {
        color: #06D001;
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .subheader {
        color: #8DECB4;
        font-size: 24px;
        margin-bottom: 20px;
    }
    .stButton button {
        background-color: #ff4b4b;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #ff1a1a;
    }
    .stSpinner > div > div {
        border-top-color: red;
        border-right-color: red;
        border-bottom-color: red;
        border-left-color: red;
    }
    .stProgress > div > div > div > div {
        background-color: red;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define the scraping function
def scrapeData(starting_date, ending_date, stock):
    symbol = stock
    fromDate = datetime.combine(starting_date, datetime.min.time())
    tillDate = datetime.combine(ending_date, datetime.min.time())
    outputPath = f"/home/ariyaman/learntocode/Stockipy/data/historical_stock_data_{symbol}.csv"
    
    def progressCallback(progress):
        progress_bar.progress(progress)

    
    niftyScrape.stock_csv(symbol, fromDate, tillDate, series="EQ", output=outputPath, show_progress=True, progress_callback=progressCallback)
    
    return outputPath

# Page title and description with animation and color
st.markdown('<h1 class="center fadeIn header">StockiPy</h1>', unsafe_allow_html=True)
st.markdown('<h3 class="center slideIn subheader">Stock Price Predictor</h3>', unsafe_allow_html=True)

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

stockExchange = {
    "NSE": "National Stock Exchange",
    "BSE": "Bombay Stock Exchange",
}

left, right = st.columns(2)

with left:
    stockSymbol = st.selectbox("Select the Stock you'd like to predict", list(nifty_50_stocks.keys()))
    companyName = nifty_50_stocks[stockSymbol]
    st.write(f"You selected: {stockSymbol} - {companyName}")

with right:
    exchangeKey = st.selectbox("Select Stock Exchange", list(stockExchange.keys()))
    exchangeName = stockExchange[exchangeKey]
    st.write(f"You selected: {exchangeKey} - {exchangeName}")

# Date input widgets for starting and ending dates
starting_date = st.date_input("Starting Date", date(2013, 1, 1))
ending_date = st.date_input("Ending Date", date(2024, 6, 27))

scrape = st.button("Scrape Data")

if scrape:
    path = scrapeData(starting_date, ending_date, stockSymbol)
    data = pd.read_csv(path)

    # Data styling
    st.dataframe(data.style.highlight_max(axis=0, color='orange'))

    # Plot the data
    fig = px.line(data, x='DATE', y='CLOSE', title=f'{stockSymbol} Closing Prices')
    st.plotly_chart(fig)
    
    st.write("You Can Now move to the Analysis Page")

    # Clean up
    folder_path = "../data"
    file_to_keep = f"historical_stock_data_{stockSymbol}.csv"
    delete_files_except_one(folder_path, file_to_keep)
