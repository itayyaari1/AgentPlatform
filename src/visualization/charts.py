import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

def prepare_chart_data(price_df: pd.DataFrame, time_interval: str, display_mode: str) -> pd.DataFrame:
    """
    Prepare data for charting based on selected interval and display mode.
    
    Args:
        price_df (pd.DataFrame): Original price data
        time_interval (str): Time interval for resampling
        display_mode (str): Display mode ('Normalized' or 'Return')
        
    Returns:
        pd.DataFrame: Processed data for charting
    """
    # Resample data based on time interval
    if time_interval == "Cumulative":
        df_resampled = price_df
    elif time_interval == "Monthly":
        df_resampled = price_df.resample("M").last()
    elif time_interval == "Quarterly":
        df_resampled = price_df.resample("Q").last()
    elif time_interval == "Yearly":
        df_resampled = price_df.resample("A").last()
    else:
        df_resampled = price_df
    
    # Process data based on display mode
    if display_mode == "Normalized":
        return df_resampled / df_resampled.iloc[0]
    else:
        return df_resampled.pct_change() * 100

def generate_chart_image(chart_data: pd.DataFrame, chart_type: str = "Line") -> BytesIO:
    """
    Generate a chart image from the data.
    
    Args:
        chart_data (pd.DataFrame): Data to plot
        chart_type (str): Type of chart ('Line' or 'Bar')
        
    Returns:
        BytesIO: Buffer containing the chart image
    """
    chart_buf = BytesIO()
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if chart_type == "Line":
        ax.plot(chart_data.index, chart_data.values)
        ax.legend(chart_data.columns)
    else:
        chart_data.plot(kind="bar", ax=ax)
    
    ax.set_title("Performance Chart")
    ax.grid(True)
    fig.tight_layout()
    
    # Save to buffer
    plt.savefig(chart_buf, format="PNG", dpi=300, bbox_inches="tight")
    chart_buf.seek(0)
    plt.close(fig)
    
    return chart_buf 