import numpy as np
import pandas as pd
import streamlit as st 
import sys 
import os
from datetime import datetime, date
from keras.models import load_model

# Add the directory containing niftyScrape.py to the Python path
sys.path.append(os.path.abspath("/home/ariyaman/learntocode/Stockipy/scraper"))

import niftyScrape

st.markdown(
    """
    <style>
    .big-font {
        font-size:50px !important;
        font-family: 'Arial', sans-serif;
        color: #4CAF50;
        text-align: center;
    }
    .spinner-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<p class="big-font"><b>Stock Market Predictor</b></p>', unsafe_allow_html=True)
left, right = st.columns(2)

with left:
    stock = st.selectbox("Select the Stock you'd like to predict ",("SBIN","HDFCBANK","AXISBANK"))
with right:
    SelectedModel = st.selectbox("Select the Machine Learning model to implement ",("LSTM (Long short-term memory)","GRU (Gated Recurrent Unit)","ARIMA (Autoregressive integrated moving average)"))

# Date input widgets for starting and ending dates
starting_date = st.date_input("Starting Date", date(2013, 1, 1))
ending_date = st.date_input("Ending Date", date(2024, 6, 27))

@st.cache_data(show_spinner=False)
def scrapedData(starting_date, ending_date, stock):
    symbol = stock
    from_date = datetime.combine(starting_date, datetime.min.time())
    to_date = datetime.combine(ending_date, datetime.min.time())
    output_path = f"/home/ariyaman/learntocode/Stockipy/data/historical_stock_data_{symbol}.csv"
    
    # Progress bar initialization
    progress_bar = st.progress(0)

    def progress_callback(progress):
        progress_bar.progress(progress)
    
    # Call the scraping function with progress callback
    niftyScrape.stock_csv(symbol, from_date, to_date, series="EQ", output=output_path, show_progress=True, progress_callback=progress_callback)
    
    st.success(f"Data scraped successfully and saved to {output_path}")
    return output_path

if st.button("Scrape Data"):
    data_path = scrapedData(starting_date, ending_date, stock)
    data = pd.read_csv(data_path)
    st.write(data)
