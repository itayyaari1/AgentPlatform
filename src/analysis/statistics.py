import pandas as pd
from ..data.stock_data import get_stock_info

def compute_statistics(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute various statistical metrics for the given price data.
    
    Args:
        price_df (pd.DataFrame): DataFrame with stock prices
        
    Returns:
        pd.DataFrame: DataFrame with computed statistics
    """
    returns = price_df.pct_change().dropna()
    stats = pd.DataFrame(index=price_df.columns)
    
    # Calculate basic statistics
    stats["Cumulative Return (%)"] = ((price_df.iloc[-1] / price_df.iloc[0]) - 1) * 100
    stats["Mean Daily Return (%)"] = returns.mean() * 100
    stats["Std Deviation (%)"] = returns.std() * 100
    stats["Variance"] = returns.var()
    
    # Calculate maximum drawdown
    drawdowns = {}
    for ticker in price_df.columns:
        prices = price_df[ticker]
        rolling_max = prices.cummax()
        drawdown = (prices - rolling_max) / rolling_max
        drawdowns[ticker] = drawdown.min() * 100
    stats["Max Drawdown (%)"] = pd.Series(drawdowns)
    
    # Add dividend yield and expense ratio
    dividends = []
    expenses = []
    for ticker in price_df.columns:
        info = get_stock_info(ticker)
        dividends.append(info["dividend_yield"] * 100 if info["dividend_yield"] else None)
        expenses.append(info["expense_ratio"] * 100 if info["expense_ratio"] else None)
    
    stats["Dividend Yield (%)"] = dividends
    stats["Expense Ratio (%)"] = expenses
    
    return stats.round(2) 