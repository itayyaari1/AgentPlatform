import streamlit as st
from PIL import Image
from src.config import BACKGROUND_STYLE  # if you are using custom background styling

# Initial page configuration – set on the main page only
st.set_page_config(page_title="BuySideAI Agent")

# Apply background style
st.markdown(BACKGROUND_STYLE, unsafe_allow_html=True)

# Load logo and title
try:
    col1, col2 = st.columns([1, 6])
    with col1:
        logo = Image.open("image.png")
        st.image(logo, width=60)
    with col2:
        st.markdown("<h1 style='margin-top: 15px;'>BuySideAI Agent</h1>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Error loading logo: {e}")

# Explanation paragraph about the site
st.write("""
Welcome to BuySideAI Agent – your advanced platform for financial analysis and fund comparison!

On this site, you can access cutting-edge tools such as:
- **Smart Stock Comparison** – get smart, detailed analysis of stocks with insightful visualizations.
- **Fund Comparison** – *In Development – Coming Soon!*
- **Chat with Agent** – *In Development – Coming Soon!*

Please use the sidebar menu to navigate between the different pages.
""")
