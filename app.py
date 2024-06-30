import numpy as np
import pandas as pd
import streamlit as st 
from datetime import date
from keras.models import load_model

model = load_model('models/LSTM/StockPredictionModel_AXIS.keras')

st.header("Stock Market Predictor")

stock = st.selectbox("Select the Stock you'd like to predict on",("SBIN (State Bank of India)","HDFC (HDFC Bank)","AXIS (Axis Bank)"))

SelectedModel =st.selectbox("Select the ml model you'd like to implement for the prediction :>",("LSTM (Long short-term memeory)","GRU (Gated Recurrent Unit)","ARIMA (Autoregressive integrated moving average)"))