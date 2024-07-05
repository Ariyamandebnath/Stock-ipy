import streamlit as st 
import os 
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Append the path to your main app for helper functions
sys.path.append(os.path.abspath("../app.py"))
from helper import get_only_file_path

st.set_page_config(page_title="Analysis", page_icon="🐍")

# Set up the page styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    .stSelectbox label {
        color: white;
    }
    .stSelectbox .st-dd .st-bq {
        background-color: #0E1117;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to get the path of the only file in the directory
directory_path = '/home/ariyaman/learntocode/Stockipy/data'
file_path = get_only_file_path(directory_path)

st.markdown("## Enhancing Your Stock Market Insights ##")

# Read the stock data
stock = pd.read_csv(file_path)
stock['DATE'] = pd.to_datetime(stock['DATE'])
stock.set_index('DATE', inplace=True)

# Dictionary for dropdown options
options_dict = {
    'Closing Price': ('CLOSE', 'blue'),
    'Volume Traded': ('VOLUME', 'green'),
    'Highest Price': ('HIGH', 'red'),
    'Last Traded Price': ('LTP', 'purple')
}

# Function to plot the selected metric
def plot_stock_metric(df, metric, color):
    fig, ax = plt.subplots(figsize=(12, 4))
    df[metric].plot(ax=ax, color=color)
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel(metric.capitalize(), color='white')
    ax.set_title(f"Stock {metric.capitalize()} Over Time", color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    st.pyplot(fig)

# Streamlit dropdown menu
option = st.selectbox(
    'Select the metric to plot:',
    list(options_dict.keys())
)

# Get the corresponding column name and color from the dictionary
selected_metric, selected_color = options_dict[option]

# Call the plotting function with the selected metric and color
plot_stock_metric(stock, selected_metric, selected_color)


# Function to plot the selected metrics
def versusGraph(df, x_metric, y_metric, color):
    # Scatter plot for custom metric comparison
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.scatter(df[x_metric], df[y_metric], color=color)
    ax.set_xlabel(x_metric.capitalize(), color='white')
    ax.set_ylabel(y_metric.capitalize(), color='white')
    ax.set_title(f"{x_metric.capitalize()} vs {y_metric.capitalize()}", color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    st.pyplot(fig)



st.markdown("### Set your matrices Stright")

left, right = st.columns(2)

# Get the corresponding column names and colors from the dictionary
with left:
    # Streamlit dropdown menus for selecting metrics
    x_option = st.selectbox(
    'Select the X-axis metric:',
    list(options_dict.keys())
)
    x_metric, _ = options_dict[x_option]
    

with right:
    y_option = st.selectbox(
    'Select the Y-axis metric:',
    list(options_dict.keys())
)
    y_metric, selected_color = options_dict[y_option]

# Call the plotting function with the selected metrics and color
versusGraph(stock, x_metric, y_metric, selected_color)



st.markdown("## Moving Averages ")


# Function to calculate SMA
def calculate_sma(df, column, period):
    sma_df = df[column].to_frame()
    sma_df[f'SMA{period}'] = df[column].rolling(period).mean()
    sma_df.dropna(inplace=True)
    return sma_df

# Streamlit dropdown menus for selecting metrics

# SMA period input
sma_period = st.number_input('Select SMA period (leave empty for no SMA):', min_value=1, max_value=365, step=1, value=30)

# Get the corresponding column names and colors from the dictionary
x_metric, _ = options_dict[x_option]
y_metric, selected_color = options_dict[y_option]

# Plot the selected metrics

# Calculate and plot SMA if specified
if sma_period:
    sma_df = calculate_sma(stock, y_metric, sma_period)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(sma_df.index, sma_df[f'SMA{sma_period}'], color='orange', linestyle='--', label=f'SMA{sma_period}')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel(y_metric.capitalize(), color='white')
    ax.set_title(f"SMA{sma_period} of {y_metric.capitalize()} Over Time", color='white')
    ax.legend()
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    st.pyplot(fig)