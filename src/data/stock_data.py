import yfinance as yf
import pandas as pd
import streamlit as st

def get_stock_data(tickers: list, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch stock data for given tickers and date range.
    
    Args:
        tickers (list): List of stock tickers
        start_date (str): Start date for data fetch
        end_date (str): End date for data fetch
        
    Returns:
        pd.DataFrame: DataFrame with stock prices
    """
    df = yf.download(tickers, start=start_date, end=end_date)
    if df.empty:
        return pd.DataFrame()
    
    try:
        if isinstance(df.columns, pd.MultiIndex):
            if "Close" in df.columns.levels[0]:
                df = df.loc[:, ("Close", slice(None))]
                df.columns = df.columns.droplevel(0)
            else:
                st.error("🔴 'Close' column not found for selected tickers.")
                return pd.DataFrame()
        else:
            df = df[["Close"]]
            df.columns = tickers
    except KeyError:
        st.error("🔴 Error accessing data columns.")
        return pd.DataFrame()
    
    return df.dropna()

def get_stock_info(ticker: str) -> dict:
    """
    Get additional information about a stock.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Dictionary containing stock information
    """
    try:
        info = yf.Ticker(ticker).info
        return {
            "dividend_yield": info.get("dividendYield", None),
            "expense_ratio": info.get("expenseRatio", None)
        }
    except:
        return {
            "dividend_yield": None,
            "expense_ratio": None
        } 