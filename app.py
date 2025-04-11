import streamlit as st
from PIL import Image
from src.config import BACKGROUND_STYLE  # if you are using custom background styling

# Initial page configuration – set on the main page only
st.set_page_config(page_title="AI Agents Platform")

# Apply background style
st.markdown(BACKGROUND_STYLE, unsafe_allow_html=True)

# Load logo and title
try:
    col1, col2 = st.columns([1, 6])
    with col1:
        logo = Image.open("image.png")
        st.image(logo, width=60)
    with col2:
        st.markdown("<h1 style='margin-top: 15px;'>AI Agents Platform</h1>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Error loading logo: {e}")

# Explanation paragraph about the site
st.write("""
Welcome to the AI Agents Platform – your central hub for accessing various AI-powered tools and assistants!

This platform brings together a diverse collection of specialized AI agents, each designed to help you with different tasks and domains. Whether you need assistance with data analysis, content creation, or specialized tasks, our AI agents are here to help.

Current available agents:
- **Financial Analysis Agent** – Get detailed financial insights and analysis
- **Agent 2** – *Coming Soon!*
- **Agent 3** – *Coming Soon!*

Use the sidebar menu to navigate between different agents and discover their unique capabilities.
""")
