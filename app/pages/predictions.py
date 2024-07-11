import streamlit as st
import numpy as np
import pandas as pd
from keras.models import load_model
import os
import sys
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error

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

# Define LSTM model prediction function
def LSTM(stockData):
    test_size = stockData[stockData.DATE.dt.year == 2023].shape[0]

    scaler = MinMaxScaler()
    scaler.fit(stockData.CLOSE.values.reshape(-1, 1))

    window_size = 60

    test_data = stockData.CLOSE[-test_size - 60:]
    test_data = scaler.transform(test_data.values.reshape(-1, 1))

    X_test = []
    y_test = []

    for i in range(window_size, len(test_data)):
        X_test.append(test_data[i - 60:i, 0])
        y_test.append(test_data[i, 0])

    X_test = np.array(X_test)
    y_test = np.array(y_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    y_test = np.reshape(y_test, (-1, 1))

    model_path = os.path.abspath("/home/ariyaman/learntocode/Stockipy/models/LSTM/StockPredictionModel.keras")

    # Load the model
    model = load_model(model_path)

    # Evaluate the model
    result = model.evaluate(X_test, y_test)
    y_pred = model.predict(X_test)
    MAPE = mean_absolute_percentage_error(y_test, y_pred)
    Accuracy = 1 - MAPE

    # Display the results using Streamlit
    st.write("Test Loss:", result)
    st.write("Test MAPE:", MAPE)
    st.write("Test Accuracy:", Accuracy)

    # Inverse transform to get the actual prices
    y_test_true = scaler.inverse_transform(y_test)
    y_test_pred = scaler.inverse_transform(y_pred)

    # Plot the results
    plt.figure(figsize=(15, 6), dpi=150)
    plt.rcParams['axes.facecolor'] = 'orange'
    plt.rc('axes', edgecolor='white')

    # Assuming 'DATE' is the column name in stockData and test_size is defined
    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_true, color='blue', lw=2)
    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_pred, color='red', lw=2)
    plt.title('Model Performance on AXIS Stock Price Prediction', fontsize=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.legend(['Actual Test Data', 'Predicted Test Data'], loc='upper left', prop={'size': 15})
    plt.grid(color='white')

    # Display the plot in Streamlit
    st.pyplot(plt)

    # Add a dropdown menu for the user to select the prediction period
    prediction_days = 30

    # Generate future predictions
    last_sequence = X_test[-1:]  # Get the last sequence from the test set
    future_predictions = []

    for _ in range(prediction_days):
        next_pred = model.predict(last_sequence)
        future_predictions.append(next_pred)
        last_sequence = np.append(last_sequence[:, 1:, :], next_pred[:, np.newaxis, :], axis=1)

    # Inverse transform to get the actual future prices
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))

    # Generate future dates
    last_date = pd.to_datetime(stockData['DATE'].iloc[-1])
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, prediction_days + 1)]

    # Create a DataFrame for future predictions
    future_predictions_df = pd.DataFrame({
        'Date': future_dates,
        'Predicted Price': future_predictions.flatten()
    })

    st.write("Closing Price for next 30 days",future_predictions_df)

    # Plot future predictions
    plt.figure(figsize=(15, 6), dpi=150)
    plt.rcParams['axes.facecolor'] = 'orange'
    plt.rc('axes', edgecolor='white')

    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_true, color='blue', lw=2)
    plt.plot(stockData['DATE'].iloc[-len(y_test_true):], y_test_pred, color='red', lw=2)
    plt.plot(future_dates, future_predictions, color='green', lw=2, linestyle='dashed')
    plt.title('Model Performance and Future Predictions on AXIS Stock Price', fontsize=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.legend(['Actual Test Data', 'Predicted Test Data', 'Future Predictions'], loc='upper left', prop={'size': 15})
    plt.grid(color='white')

    # Display the future predictions plot in Streamlit
    st.pyplot(plt)


def GRU(stockData):
    return



def main():
    # Bring data of the previously loaded stock from the local storage for prediction
    directory_path = '/home/ariyaman/learntocode/Stockipy/data'
    file_path = get_only_file_path(directory_path)

    # Read the stock data
    stockData = pd.read_csv(file_path)
    stockData['DATE'] = pd.to_datetime(stockData['DATE'])
    stockData.sort_values(by='DATE', ascending=True, inplace=True)
    stockData.reset_index(drop=True, inplace=True)

    # Page heading and introduction
    st.markdown('<h1 class="stTitle">Stock Market Forecasting Insights</h1>', unsafe_allow_html=True)
    st.markdown("""
    ### Predict Stock Prices with Machine Learning Models

    Harness the power of ML models of your choice to forecast stock prices with precision and confidence. Choose from a selection of advanced machine learning models to tailor your predictions based on historical data.
    Explore and compare different models to uncover insights that drive your investment strategies forward.
    """)

    # Define machine learning models
    ml_model = {
        "LSTM": "Long Short-Term Memory",
        "GRU": "Gated Recurrent Unit",
        "ARIMA": "AutoRegressive Integrated Moving Average"
    }

    # Display model selection and get the selected model key
    selected_model_key, selected_model_name = display_model_selection(ml_model)

    # Plot stock price history
    fig = px.line(stockData, x='DATE', y='CLOSE')
    fig.update_traces(line_color='black')
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Scaled Price",
        title={'text': f"{stockData['SYMBOL'].iloc[0]} Price History Data", 'y': 0.95, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'},
        plot_bgcolor='rgba(255,223,0,0.8)'
    )
    st.plotly_chart(fig)

    # Call the selected model function
    if selected_model_key == "LSTM":
        LSTM(stockData)
    elif selected_model_key == "GRU":
        st.write("GRU model prediction function is not yet implemented.")
    elif selected_model_key == "ARIMA":
        st.write("ARIMA model prediction function is not yet implemented.")

if __name__ == "__main__":
    main()
