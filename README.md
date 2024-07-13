
# Stockipy

Stockipy is a comprehensive project designed to scrape stock data, perform exploratory data analysis (EDA), and implement multiple machine learning models to predict stock closing prices. The project includes an LSTM, GRU, and ARIMA model to compare the accuracy and losses of each. The results are presented through a multipage Streamlit application.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Modules](#modules)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Data Scraping:** Scrape stock data from various sources.
- **Exploratory Data Analysis (EDA):** Analyze the collected data for insights and trends.
- **Machine Learning Models:** Implement LSTM, GRU, and ARIMA models to predict stock closing prices.
- **Model Comparison:** Compare the accuracy and losses of each model.
- **Streamlit Application:** Interactive multipage Streamlit app to present data and predictions.



## Video Demo

Watch the demo video below to see Stockipy in action:

https://github.com/user-attachments/assets/37727060-e560-44f6-bde2-7a90ab65901b



## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/Ariyamandebnath/Stock-ipy
    cd stockipy
    ```

2. **Create and activate a virtual environment (optional but recommended):**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. **Locate to app folder:**
    ```sh
    cd app
    ```


2. **Run the Streamlit application:**

    ```sh
    streamlit run app.py
    ```

## Project Structure
```
Stockipy/
├── analysis/
│ └── EDA.ipynb
├── app/
│ └── pages/
| │ ├── Analysis.py
| │ └── prediction.py
│ ├── app.py
│ └── helper.py
├── data/
│ └── temporary_Storage
├── models/
│ ├── ARIMA/
| │ ├── arima.pkl
| │ ├── AXIS_arima.pkl
| │ ├── HDFC_arima.pkl
| │ └── SBIN_arima.pkl
│ ├── GRU/
| │ ├── AXIS_MODEL_GRU.keras
| │ ├── HDFC_MODEL_GRU.keras
| │ └── SBIN_MODEL_GRU.keras
│ └── LSTM/
| │ ├── StockPredictionModel_AXIS.keras
| │ ├── StockPredictionModel_AXIS.keras
| │ └── StockPredictionModel_AXIS.keras
├── predictions
│ └── ARIMA.ipynb
│ └── GRU.ipynb
│ └── LSTM.ipynb
├── scraper
│ └── niftyScraper.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Modules

- **scraper.py:** Script to scrape stock data from various sources.
- **eda.py:** Script to perform exploratory data analysis on the collected data.
- **train_models.py:** Script to train and evaluate LSTM, GRU, and ARIMA models.
- **app.py:** Streamlit application to present data and predictions.

## Contributing

Contributions are welcome! Please read the `CONTRIBUTING.md` for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

