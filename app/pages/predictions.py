import streamlit as st
import numpy as np
import pandas as pd
from keras.models import load_model
import pickle
import os
import sys
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima

# Add path to the helper module
sys.path.append(os.path.abspath("../app.py"))
from helper import get_only_file_path

# Set page configuration and custom styling
st.set_page_config(page_title="Prediction", page_icon="🐍")

# Custom CSS styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: white;
        text-align: center;
    }
    .stSelectbox label {
        color: white;
        text-align: center;
    }
    .stSelectbox .st-dd .st-bq {
        background-color: #0E1117;
        color: white;
        text-align: center;
    }
    .stMarkdown {
        color: white;
        text-align: center;
    }
    .stMarkdown h1,.stMarkdown h2 {
        color: #DEF9C4 !important;
        text-align: center;
    }
    .stMarkdown h3 {
        color: #50B498 !important;
        text-align: center;
    }
    .stTitle {
        color: #DEF9C4;  /* Title color */
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
    }
    .stButton button {
        color: #304463 !important;
        border-color: #304463 !important;
        background-color: #EEEDEB;  /* Button background color */
        transition: all 0.3s ease;
        text-align: center;
        font-size: 16px; /* Adjust the font size as needed */
        font-weight: bold; /* Adjust the font weight as needed */
    }

    .stButton button:hover {
        background-color: #FFD700;  /* Button hover background color */
    }

    .stButton button:active {
        transform: scale(0.95);
    }

    </style>
    """,
    unsafe_allow_html=True
)


def display_model_selection(ml_model):
    modelKey = ""

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("LSTM"):
            modelKey = "LSTM"
    with col2:
        if st.button("GRU"):
            modelKey = "GRU"
    with col3:
        if st.button("ARIMA"):
            modelKey = "ARIMA"

    if modelKey:
        modelName = ml_model[modelKey]
        st.write(f"You selected: {modelKey} - {modelName}")
        return modelKey, modelName
    return None, None


def common_prediction(stockData, model_path, model_type, scaler, window_size=60, prediction_days=30):
    test_size = stockData[stockData.DATE.dt.year == 2023].shape[0]

    test_data = stockData.CLOSE[-test_size - window_size:]
    test_data = scaler.transform(test_data.values.reshape(-1, 1))

    X_test = []
    y_test = []

    for i in range(window_size, len(test_data)):
        X_test.append(test_data[i - window_size:i, 0])
        y_test.append(test_data[i, 0])

    X_test = np.array(X_test)
    y_test = np.array(y_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    y_test = np.reshape(y_test, (-1, 1))

    if model_type in ['LSTM', 'GRU']:
        path = os.path.abspath(model_path)

        model = load_model(path)
        result = model.evaluate(X_test, y_test)
        y_pred = model.predict(X_test)
    elif model_type == 'ARIMA':
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        y_pred = model.forecast(steps=len(y_test))[0]
        y_pred = y_pred.reshape(-1, 1)

    MAPE = mean_absolute_percentage_error(y_test, y_pred)
    Accuracy = 1 - MAPE

    st.write("Test MAPE:", MAPE)
    st.write("Test Accuracy:", Accuracy)

    y_test_true = scaler.inverse_transform(y_test)
    y_test_pred = scaler.inverse_transform(y_pred)

    plt.figure(figsize=(15, 6), dpi=150)
    plt.rcParams['axes.facecolor'] = 'orange'
    plt.rc('axes', edgecolor='white')

    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_true, color='blue', lw=2)
    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_pred, color='red', lw=2)
    plt.title(f'Model Performance on {stockData["SYMBOL"].iloc[0]} Stock Price Prediction', fontsize=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.legend(['Actual Test Data', 'Predicted Test Data'], loc='upper left', prop={'size': 15})
    plt.grid(color='white')
    st.pyplot(plt)

    last_sequence = X_test[-1:] if model_type in ['LSTM', 'GRU'] else stockData.CLOSE[-window_size:].values.reshape(-1, 1)
    future_predictions = []

    for _ in range(prediction_days):
        if model_type in ['LSTM', 'GRU']:
            next_pred = model.predict(last_sequence)
            future_predictions.append(next_pred)
            last_sequence = np.append(last_sequence[:, 1:, :], next_pred[:, np.newaxis, :], axis=1)
        elif model_type == 'ARIMA':
            next_pred = model.forecast(steps=1)[0]
            future_predictions.append(next_pred)
            last_sequence = np.append(last_sequence[1:], next_pred.reshape(-1, 1), axis=0)

    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    last_date = pd.to_datetime(stockData['DATE'].iloc[-1])
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, prediction_days + 1)]

    future_predictions_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted Price': future_predictions.flatten()
    })

    st.write(f"Closing Price for next {prediction_days} days", future_predictions_df)

    plt.figure(figsize=(15, 6), dpi=150)
    plt.rcParams['axes.facecolor'] = 'orange'
    plt.rc('axes', edgecolor='white')

    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_true, color='blue', lw=2)
    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_pred, color='red', lw=2)
    plt.plot(future_dates, future_predictions, color='green', lw=2, linestyle='dashed')
    plt.title(f'Model Performance and Future Predictions on {stockData["SYMBOL"].iloc[0]} Stock Price', fontsize=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.legend(['Actual Test Data', 'Predicted Test Data', 'Future Predictions'], loc='upper left', prop={'size': 15})
    plt.grid(color='white')
    st.pyplot(plt)


def ARIMA(stockData):
    df2 = stockData.set_index('DATE')
    data = list(df2["CLOSE"])
    x_train = data[:-100]
    x_test = data[-100:]

    # Load the ARIMA model from pickle file
    pickle_file_path = "../models/ARIMA/HDFC_ARIMA.pkl"  # Adjust this path
    with open(pickle_file_path, 'rb') as f:
        model = pickle.load(f)

    # Make predictions
    start = len(x_train)
    end = len(x_train) + len(x_test) - 1
    pred = model.predict(start=start, end=end)

    # Prepare the predicted series
    s = pd.Series(pred, index=df2.index[-100:])

    # Plot actual vs predicted
    plt.figure(figsize=(10, 6), dpi=100)
    df2['CLOSE'][-100:].plot(label='Actual Stock Price', legend=True)
    s.plot(label='Predicted Price', legend=True)
    plt.title(f'Model Performance on {stockData["SYMBOL"].iloc[0]} Stock Price Prediction (ARIMA)', fontsize=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.legend(prop={'size': 15})
    plt.grid(color='white')

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Calculate metrics (MAPE and Accuracy)
    y_test = df2['CLOSE'][-100:].values  # Ensure y_test is 1-dimensional
    y_test_pred = s.values  # Ensure y_test_pred is 1-dimensional
    MAPE = mean_absolute_percentage_error(y_test, y_test_pred)
    Accuracy = 1 - MAPE

    # Display metrics in Streamlit
    st.write("Test MAPE:", MAPE)
    st.write("Test Accuracy:", Accuracy)

    pred_future = model.predict(start=end, end=end + 10)


def main():
    # Load data
    directory_path = '../data'
    file_path = get_only_file_path(directory_path)
    stockData = pd.read_csv(file_path)
    stockData['DATE'] = pd.to_datetime(stockData['DATE'])
    stockData.sort_values(by='DATE', ascending=True, inplace=True)
    stockData.reset_index(drop=True, inplace=True)

    # Display introductory content
    st.markdown('<h1 class="stTitle">Stock Market Forecasting Insights</h1>', unsafe_allow_html=True)
    st.markdown("""
    ### Predict Stock Prices with Machine Learning Models

    Harness the power of ML models of your choice to forecast stock prices with precision and confidence. Choose from a selection of advanced machine learning models to tailor your predictions based on historical data.
    Explore and compare different models to uncover insights that drive your investment strategies forward.
    """)

    # Display historical price plot
    fig = px.line(stockData, x='DATE', y='CLOSE')
    fig.update_traces(line_color='black')
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Scaled Price",
        title={'text': f"{stockData['SYMBOL'].iloc[0]} Price History Data", 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        plot_bgcolor='rgba(255,223,0,0.8)'
    )
    st.plotly_chart(fig)

    # Model selection and prediction
    ml_model = {
        "LSTM": "Long Short-Term Memory",
        "GRU": "Gated Recurrent Unit",
        "ARIMA": "AutoRegressive Integrated Moving Average"
    }
    selected_model_key, selected_model_name = display_model_selection(ml_model)

    # Define model paths
    model_paths = {
        "LSTM": "../models/LSTM/StockPredictionModel_AXIS.keras",
        "GRU": "../models/GRU/AXIS_Model_GRU.keras",
        "ARIMA": "../models/ARIMA/arima.pkl"
    }

    # Perform predictions based on selected model
    if selected_model_key:
        if selected_model_key in ["LSTM", "GRU"]:
            scaler = MinMaxScaler()
            scaler.fit(stockData.CLOSE.values.reshape(-1, 1))
            common_prediction(stockData, model_paths[selected_model_key], selected_model_key, scaler)
        elif selected_model_key == "ARIMA":
            ARIMA(stockData)


if __name__ == '__main__':
    main()
