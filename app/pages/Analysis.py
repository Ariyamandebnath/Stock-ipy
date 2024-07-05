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
    'Closing Price': ('CLOSE', '#96C9F4'),
    'Volume Traded': ('VOLUME', '#9CDBA6'),
    'Highest Price': ('HIGH', '#FF6969'),
    'Last Traded Price': ('LTP', '#FFC7ED')
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

# dropdown for the first symbolic graph
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





# Function to calculate SMA
def calculate_SMA(df, column):
    sma_df = df[column].to_frame()
    sma_df['SMA30'] = df[column].rolling(30).mean()
    sma_df.dropna(inplace=True)
    return sma_df

def calculate_CMA(df, column):
    cma_df = df[column].to_frame()
    cma_df['CMA30'] = df[column].expanding().mean()
    cma_df.dropna(inplace=True)
    return cma_df

def calculate_EMA(df, column):
    ema_df = df[f"{column}"].to_frame()
    ema_df['EMA30'] = df[column].ewm(span=30).mean()
    ema_df.dropna(inplace=True)
    return ema_df

moving_averages = {
    "SMA": ("Simple Moving Average", "A SMA tells us the unweighted mean of the previous K data points, The more the value of K the more smooth is the curve, but increasing K decreases accuracy. If the data points are p1,  p2, . . . , pn then we calculate the simple moving average."),
    
    "CMA": ("Cumulative Moving Average", "CMA is the mean of all the previous values up to the current value.CMA of dataPoints x1, x2 …..  at time t can be calculated as,the summation of all x's divided by time t."),
    
    "EMA": ("Exponential Moving Average", "EMA tells us the weighted mean of the previous K data points.EMA places a greater weight and significance on the most recent data points.")
}

st.title('Moving Average Calculator')

left , right = st.columns(2)

with left:
    selected_metric = st.selectbox('Select Metric:', ['CLOSE', 'VOLUME']) 

with right:
    selected_ma_type = st.selectbox('Select Moving Average Type:', list(moving_averages.keys()), format_func=lambda x: moving_averages[x][0])

if selected_ma_type:
    st.markdown(f"**{moving_averages[selected_ma_type][0]}**: {moving_averages[selected_ma_type][1]}")
    
    
# Calculate selected moving average
ma_df = None
if selected_ma_type == 'SMA':
    ma_df = calculate_SMA(stock, selected_metric)
elif selected_ma_type == 'CMA':
    ma_df = calculate_CMA(stock, selected_metric)
elif selected_ma_type == 'EMA':
    ma_df = calculate_EMA(stock, selected_metric)

# Plotting
if ma_df is not None:
    st.subheader(f'{moving_averages[selected_ma_type][0]} for {selected_metric}')
    fig, ax = plt.subplots(figsize=(10, 6))  # Create a new figure and axis
    ax.plot(ma_df.index, ma_df[selected_metric], label=selected_metric)
    ax.plot(ma_df.index, ma_df[f'{selected_ma_type}30'], label=f'{moving_averages[selected_ma_type][0]} (30 days)')
    ax.set_xlabel('Date')
    ax.set_ylabel(selected_metric)
    ax.legend()
    st.pyplot(fig) 
else:
    st.write("Select valid options to generate the plot.")