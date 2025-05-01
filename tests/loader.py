import pytest
import pandas as pd
from option_greeks_dashboard.data.loader import fetch_historical_prices

def test_fetch_historical_prices(monkeypatch):
    # monkeypatch yfinance to return a fake DataFrame
    class DummyTicker:
        def history(self, period):
            return pd.DataFrame({"Close":[1,2,3]}, index=pd.date_range("2025-01-01", periods=3))

    monkeypatch.setattr("yfinance.Ticker", lambda ticker: DummyTicker())
    df = fetch_historical_prices("FAKE", period="1d")
    assert list(df.columns) == ["Date", "Close"]
    assert df.shape == (3, 2)
