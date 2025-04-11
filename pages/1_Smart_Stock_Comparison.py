import streamlit as st
from datetime import date, timedelta
from PIL import Image

from src.config import BACKGROUND_STYLE
from src.visualization.charts import prepare_chart_data, generate_chart_image
from src.agents.stocks_agent import FinancialAgent

# Apply background style
st.markdown(BACKGROUND_STYLE, unsafe_allow_html=True)

# Load logo and title
try:
    col1, col2 = st.columns([1, 6])
    with col1:
        logo = Image.open("image.png")
        st.image(logo, width=60)
    with col2:
        st.markdown("<h1 style='margin-top: 15px;'>Smart Stock Comparison</h1>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Error loading logo: {e}")

# Create an instance of the FinancialAgent
agent = FinancialAgent(language="en")

# Initialize session state for storing analysis results and chart options
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'result' not in st.session_state:
    st.session_state.result = None
if 'chart_time_interval' not in st.session_state:
    st.session_state.chart_time_interval = "Cumulative"
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = "Line"
if 'chart_display_mode' not in st.session_state:
    st.session_state.chart_display_mode = "Normalized"

# Input form for tickers and dates
with st.form("stock_form"):
    tickers_input = st.text_input(
        "Enter stock tickers (comma-separated):",
        "AAPL, MSFT, TSLA"
    )
    start_date = st.date_input(
        "Start Date",
        date.today() - timedelta(days=365)
    )
    end_date = st.date_input(
        "End Date",
        date.today()
    )
    submitted = st.form_submit_button("Compare")

# Process the form submission and store results in session state
if submitted:
    with st.spinner("Analyzing data..."):
        result = agent.analyze_stocks(tickers_input)
        st.session_state.result = result
        st.session_state.analyzed = True

# Display analysis results if available
if st.session_state.analyzed and st.session_state.result is not None:
    result = st.session_state.result
    
    if "error" in result:
        st.error(result["error"])
    else:
        # Display statistics table
        st.subheader("Table")
        st.dataframe(result["stats_table"])
        
        # Generate and display chart based on the price data returned by the agent
        if "price_df" in result:
            price_df = result["price_df"]
            
            # Section for chart
            st.subheader("Chart")
            
            # Chart options with columns for compact layout
            col1, col2, col3 = st.columns(3)
            
            # Time interval selection
            with col1:
                time_options = ["Cumulative", "Monthly", "Quarterly", "Yearly"]
                time_interval = st.selectbox(
                    "Time Interval",
                    time_options,
                    index=time_options.index(st.session_state.chart_time_interval) if st.session_state.chart_time_interval in time_options else 0
                )
                st.session_state.chart_time_interval = time_interval
            
            # Chart type selection
            with col2:
                chart_options = ["Line", "Bar"]
                chart_type = st.radio(
                    "Chart Type",
                    chart_options,
                    index=chart_options.index(st.session_state.chart_type) if st.session_state.chart_type in chart_options else 0,
                    horizontal=True
                )
                st.session_state.chart_type = chart_type
            
            # Display mode selection
            with col3:
                display_options = ["Normalized", "Return"]
                display_mode = st.radio(
                    "Display Mode",
                    display_options,
                    index=display_options.index(st.session_state.chart_display_mode) if st.session_state.chart_display_mode in display_options else 0,
                    horizontal=True
                )
                st.session_state.chart_display_mode = display_mode
            
            # Prepare and display chart data
            chart_data = prepare_chart_data(price_df, time_interval, display_mode)
            
            # Show the chart based on selected type
            if chart_type == "Line":
                st.line_chart(chart_data)
            else:
                st.bar_chart(chart_data)
            
            # Generate chart image for PDF export
            chart_image = generate_chart_image(chart_data, chart_type)
        else:
            st.warning("Price data not available for chart generation.")
        
        # Display Smart Analysis text
        st.subheader("Smart Analysis")
        st.markdown(result["analysis_text"])
        
        # PDF download button
        st.download_button(
            label="📄 Export to PDF",
            data=result["pdf_report"].getvalue(),
            file_name="financial_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf_button"
        )
