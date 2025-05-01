import pandas as pd
import yfinance as yf

def fetch_historical_prices(ticker: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetches historical daily closing prices for the given ticker.
    Returns a DataFrame with columns ['Date', 'Close'] indexed by Date.
    """
    df = yf.Ticker(ticker).history(period=period)[["Close"]]
    df.index.name = "Date"
    return df.reset_index()

