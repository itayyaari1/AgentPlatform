import streamlit as st
from datetime import date, timedelta
from PIL import Image

from src.config import BACKGROUND_STYLE
from src.data.stock_data import get_stock_data
from src.analysis.statistics import compute_statistics
from src.ai.analysis import get_ai_analysis
from src.visualization.charts import prepare_chart_data, generate_chart_image
from src.utils.pdf_generator import generate_pdf_report

# שימו לב: אין כאן קריאה ל-st.set_page_config – כבר הוגדרה בדף הראשי (app.py) או בסדר הנכון
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

language = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)

with st.form("stock_form"):
    tickers = st.text_input(
        "הזן טיקרי מניות (מופרדים בפסיק):" if language=="עברית" else "Enter stock tickers (comma-separated):",
        "AAPL, MSFT, TSLA"
    )
    start_date = st.date_input(
        "תאריך התחלה" if language=="עברית" else "Start Date",
        date.today() - timedelta(days=365)
    )
    end_date = st.date_input(
        "תאריך סיום" if language=="עברית" else "End Date",
        date.today()
    )
    submitted = st.form_submit_button("השווה" if language=="עברית" else "Compare")

if submitted:
    tickers_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    price_df = get_stock_data(tickers_list, start_date, end_date)
    
    if price_df.empty:
        st.error("❌ " + ("לא נמצאו נתונים לטיקר שנבחר או שהתרחשה שגיאה בהורדה." if language=="עברית" else "No data found for selected tickers or an error occurred."))
    else:
        st.session_state["price_df"] = price_df

if "price_df" in st.session_state:
    price_df = st.session_state["price_df"]
    
    st.subheader("אפשרויות גרף" if language=="עברית" else "Chart Options")
    
    if language == "עברית":
        time_options = {"מצטבר": "Cumulative", "חודשי": "Monthly", "רבעוני": "Quarterly", "שנתי": "Yearly"}
        selected_time_label = st.selectbox("בחר חתך זמן", list(time_options.keys()), key="time_interval")
        selected_time_interval = time_options[selected_time_label]
    else:
        selected_time_interval = st.selectbox(
            "Select Time Interval",
            ["Cumulative", "Monthly", "Quarterly", "Yearly"],
            key="time_interval"
        )
    
    selected_chart_type = st.radio(
        "בחר סוג גרף" if language=="עברית" else "Select chart type",
        ["Line", "Bar"],
        key="chart_type"
    )
    selected_display_mode = st.radio(
        "בחר מצב תצוגה" if language=="עברית" else "Select display mode",
        ["Normalized", "Return"],
        key="display_mode"
    )
    
    chart_data = prepare_chart_data(price_df, selected_time_interval, selected_display_mode)
    st.subheader("גרף" if language=="עברית" else "Chart")
    if selected_chart_type == "Line":
        st.line_chart(chart_data)
    else:
        st.bar_chart(chart_data)
    
    stats = compute_statistics(price_df)
    st.subheader("טבלה" if language=="עברית" else "Table")
    st.dataframe(stats)
    
    st.subheader("ניתוח חכם" if language=="עברית" else "Smart Analysis")
    summary_text = stats.to_csv()
    if summary_text.strip() != "":
        lang_code = "he" if language=="עברית" else "en"
        ai_analysis = get_ai_analysis(summary_text, language=lang_code)
        
        if language == "עברית":
            st.markdown(f"<div dir='rtl' style='text-align: right;'>{ai_analysis}</div>", unsafe_allow_html=True)
        else:
            st.markdown(ai_analysis)
    
    chart_image = generate_chart_image(chart_data, selected_chart_type)
    
    st.download_button(
        label="📄 ייצוא ל-PDF" if language=="עברית" else "📄 Export to PDF",
        data=generate_pdf_report(stats, ai_text=ai_analysis, chart_image=chart_image),
        file_name="financial_report.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_pdf_button"
    )
