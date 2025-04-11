import streamlit as st
from src.config import BACKGROUND_STYLE
from src.agents.stocks_agent import FinancialAgent

def main():
    st.markdown(BACKGROUND_STYLE, unsafe_allow_html=True)
    st.header("שיחה עם הסוכן")

    # יצירת מופע סוכן
    agent = FinancialAgent(language="he")  # או כמובן לנהל את השפה אחרת
    
    # אזור השיחה
    chat_input = st.text_area("שאל את הסוכן:", "מהם הסיכונים בהשקעה במניות אלו?")
    if st.button("שלח שאלה", key="chat_button"):
        chat_response = agent.chat_with_agent(chat_input)
        st.write("תשובת הסוכן:")
        st.write(chat_response)
