# financial_agent_app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import date, timedelta
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
from fpdf import FPDF
import tempfile

# הזרקת CSS לעיצוב כהה עם רקע גלקסיה (מתאים לגרסאות העדכניות)
st.markdown(
    """
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1517816743773-6e0fd518b4a6?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80") no-repeat center center fixed;
        background-size: cover;
    }
    /* שינוי רקע הקונטיינר הראשי לרקע שקוף כהה */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(0, 0, 0, 0.7);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Together AI setup ---
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"

# --- פונקציות חישוב ---
def get_data(tickers, start_date, end_date):
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

def compute_stats(price_df):
    returns = price_df.pct_change().dropna()
    stats = pd.DataFrame(index=price_df.columns)
    stats["Cumulative Return (%)"] = ((price_df.iloc[-1] / price_df.iloc[0]) - 1) * 100
    stats["Mean Daily Return (%)"] = returns.mean() * 100
    stats["Std Deviation (%)"] = returns.std() * 100
    stats["Variance"] = returns.var()

    drawdowns = {}
    for ticker in price_df.columns:
        prices = price_df[ticker]
        rolling_max = prices.cummax()
        drawdown = (prices - rolling_max) / rolling_max
        drawdowns[ticker] = drawdown.min() * 100
    stats["Max Drawdown (%)"] = pd.Series(drawdowns)

    # Attempt to add dividend yield and expense ratio from yf.Ticker
    dividends = []
    expenses = []
    for ticker in price_df.columns:
        try:
            info = yf.Ticker(ticker).info
            dividends.append(info.get("dividendYield", None) * 100 if info.get("dividendYield") else None)
            expenses.append(info.get("expenseRatio", None) * 100 if info.get("expenseRatio") else None)
        except:
            dividends.append(None)
            expenses.append(None)
    stats["Dividend Yield (%)"] = dividends
    stats["Expense Ratio (%)"] = expenses

    return stats.round(2)

def ask_ai(summary, language="he"):
    if language == "he":
        system_prompt = "אתה יועץ פיננסי חכם. ענה בעברית בניתוח מקצועי וידידותי על הנתונים שהוזנו."
        user_prompt = f"הנה נתונים על מניות בטבלה (CSV):\n\n{summary}\n\nנתח את הנתונים והסבר למשתמש את הביצועים והסטטיסטיקות החשובות."
    else:
        system_prompt = "You are a smart financial advisor. Respond in English with a friendly and professional analysis."
        user_prompt = f"Here is a table (CSV) with stock statistics:\n\n{summary}\n\nPlease analyze it and explain the key metrics to the user."
    
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        res = requests.post(TOGETHER_API_URL, headers=headers, json=payload)
        res_json = res.json()
        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"]
        elif "error" in res_json:
            return f"Server error: {res_json['error']}"
        else:
            return f"Unexpected response: {res_json}"
    except Exception as e:
        return f"Error contacting AI: {e}"

def generate_pdf(stats_df, ai_text=None, chart_image=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="BuySideAI Financial Report", ln=True, align='C')
    pdf.ln(10)

    # Add table header
    pdf.set_fill_color(230, 230, 250)
    for col in stats_df.columns:
        pdf.cell(40, 10, col, border=1, fill=True)
    pdf.ln()

    # Add table rows
    for idx, row in stats_df.iterrows():
        for val in row:
            text = str(val) if val is not None else "-"
            pdf.cell(40, 10, text[:15], border=1)
        pdf.ln()

    # Add AI analysis if provided
    if ai_text:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="AI Analysis:", ln=True)
        pdf.set_font("Arial", size=11)
        for line in ai_text.split('\n'):
            pdf.multi_cell(0, 10, line)

    # Add chart image if provided
    if chart_image:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_file.write(chart_image.getvalue())
            tmp_file.flush()
            tmp_path = tmp_file.name
        pdf.add_page()
        pdf.image(tmp_path, x=10, y=30, w=180)
        os.remove(tmp_path)

    pdf_output = pdf.output(dest="S").encode("latin1")
    return BytesIO(pdf_output)

# --- UI ---

# טעינת הלוגו והכותרת
try:
    col1, col2 = st.columns([1, 6])
    with col1:
        logo = Image.open("image.png")
        st.image(logo, width=60)
    with col2:
        st.markdown("""<h1 style='margin-top: 15px;'>BuySideAI Agent</h1>""", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Error loading logo: {e}")

# בחירת שפה
language = st.radio("Language / שפה", ["English", "עברית"], horizontal=True)

# טופס להזנת נתונים בסיסיים – לאחר לחיצה על Compare, הנתונים נשמרים ב-session_state
with st.form("stock_form"):
    tickers = st.text_input("הזן טיקרי מניות (מופרדים בפסיק):" if language=="עברית" else "Enter stock tickers (comma-separated):", "AAPL, MSFT, TSLA")
    start_date = st.date_input("תאריך התחלה" if language=="עברית" else "Start Date", date.today() - timedelta(days=365))
    end_date = st.date_input("תאריך סיום" if language=="עברית" else "End Date", date.today())
    submitted = st.form_submit_button("השווה" if language=="עברית" else "Compare")

if submitted:
    tickers_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    price_df = get_data(tickers_list, start_date, end_date)
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
        selected_time_interval = st.selectbox("Select Time Interval", ["Cumulative", "Monthly", "Quarterly", "Yearly"], key="time_interval")
    
    selected_chart_type = st.radio("בחר סוג גרף" if language=="עברית" else "Select chart type", ["Line", "Bar"], key="chart_type")
    selected_display_mode = st.radio("בחר מצב תצוגה" if language=="עברית" else "Select display mode", ["Normalized", "Return"], key="display_mode")
    
    # עיבוד הנתונים לפי חתך הזמן
    if selected_time_interval == "Cumulative":
        df_resampled = price_df
    elif selected_time_interval == "Monthly":
        df_resampled = price_df.resample("M").last()
    elif selected_time_interval == "Quarterly":
        df_resampled = price_df.resample("Q").last()
    elif selected_time_interval == "Yearly":
        df_resampled = price_df.resample("A").last()
    else:
        df_resampled = price_df
    
    # חישוב נתוני הגרף בהתאם למצב התצוגה
    if selected_display_mode == "Normalized":
        chart_data = df_resampled / df_resampled.iloc[0]
    else:
        chart_data = df_resampled.pct_change() * 100

    st.subheader("גרף" if language=="עברית" else "Chart")
    chart_placeholder = st.empty()
    with chart_placeholder:
        if selected_chart_type == "Line":
            st.line_chart(chart_data)
        else:
            st.bar_chart(chart_data)
    
    stats = compute_stats(df_resampled)
    st.subheader("טבלה" if language=="עברית" else "Table")
    st.dataframe(stats)
    
    st.subheader("ניתוח חכם" if language=="עברית" else "Smart Analysis")
    ai_analysis = None
    if TOGETHER_API_KEY:
        summary_text = stats.to_csv()
        if summary_text.strip() != "":
            lang_code = "he" if language=="עברית" else "en"
            ai_analysis = ask_ai(summary_text, language=lang_code)
            if language == "עברית":
                st.markdown(f"<div dir='rtl' style='text-align: right;'>{ai_analysis}</div>", unsafe_allow_html=True)
            else:
                st.markdown(ai_analysis)
        else:
            st.warning("⚠️ " + ("הטבלה ריקה, לא נשלחה שאלה ל-AI." if language=="עברית" else "Stats table is empty. Nothing was sent to AI."))
    else:
        st.warning("⚠️ " + ("לא נמצא מפתח Together AI. אנא הגדר TOGETHER_API_KEY בסביבת הפיתוח." if language=="עברית" else "TOGETHER_API_KEY not found. Please set it in your environment."))
    
    # יצירת גרף כתמונה לפי הבחירות
    chart_buf = BytesIO()
    fig, ax = plt.subplots()
    if selected_chart_type == "Line":
        ax.plot(chart_data.index, chart_data.values)
    else:
        chart_data.plot(kind="bar", ax=ax)
    ax.set_title("גרף תשואה" if language=="עברית" else "Return Chart")
    fig.tight_layout()
    fig.savefig(chart_buf, format="PNG")
    chart_buf.seek(0)
    
    st.download_button(
        label="📄 ייצוא ל-PDF" if language=="עברית" else "📄 Export to PDF",
        data=generate_pdf(stats, ai_text=ai_analysis, chart_image=chart_buf),
        file_name="financial_report.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_pdf_button"
    )
